import argparse

import torch

from xlpersona.conditions import CONDITIONS
from xlpersona.data import load_requests
from xlpersona.geometry import boot_geometry
from xlpersona.hooks import Resid
from xlpersona.io import OUT, log, write_json
from xlpersona.model import last_resid, load
from xlpersona.prompts import stage1_prompt_sets, stage2_prompt_sets
from xlpersona.templates import load_templates

GAPS = [("hi", "hi_rom"), ("hi", "hi_cm"), ("ne", "ne_rom"), ("ne", "ne_cm"), ("hi_cm", "hi_rom"), ("ne_cm", "ne_rom")]


def analyze(find, test, lstar, rand, path):
    res = boot_geometry(find, test, ref="en", gaps=GAPS, B=2000, seed=0, rand=rand)
    res["lstar"] = lstar
    write_json(res, path)
    for c in find:
        p, ci = res["point"][c], res["ci"][c]
        log(c, {k: round(v, 3) for k, v in p.items()}, "R CI", [round(x, 3) for x in ci["R"]])
    for k, v in res["gaps"].items():
        log("gap", k, {m: [round(x, 3) for x in ci] for m, ci in v.items()})
    return res


def main():
    out = OUT / "main"
    D = torch.load(out / "directions.pt", map_location="cpu", weights_only=False)
    lstar = D["lstar"]
    tok, model = load(device="cuda")
    hook = Resid(model)
    rows, ts = load_requests(), load_templates()
    s1 = stage1_prompt_sets(rows, ts)

    def acts(texts):
        return last_resid(tok, model, hook, texts, bs=32)[:, lstar].float().cpu()

    find, test = {}, {}
    for c in CONDITIONS:
        find[c] = (acts([p.text for p in s1 if p.cond == c and p.template]),
                   acts([p.text for p in s1 if p.cond == c and p.template is None and p.harmful]))
        s2 = stage2_prompt_sets(rows, ts, c)
        test[c] = (acts([p.text for p in s2["persona_test"]]), acts([p.text for p in s2["plain_test"]]))
        log(c, "find", tuple(find[c][0].shape), tuple(find[c][1].shape), "test", tuple(test[c][0].shape))
    torch.save({"lstar": lstar, "find": {c: (P.half(), Q.half()) for c, (P, Q) in find.items()},
                "test": {c: (P.half(), Q.half()) for c, (P, Q) in test.items()}}, out / "acts_lstar.pt")
    analyze(find, test, lstar, D["unit"]["rand"][lstar], out / "geometry.json")


def main_local(acts, directions, path):
    A = torch.load(acts, weights_only=False)
    rand = torch.load(directions, map_location="cpu", weights_only=False)["unit"]["rand"][A["lstar"]]
    f = {c: (P.float(), Q.float()) for c, (P, Q) in A["find"].items()}
    t = {c: (P.float(), Q.float()) for c, (P, Q) in A["test"].items()}
    analyze(f, t, A["lstar"], rand, path)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--acts")
    ap.add_argument("--directions")
    ap.add_argument("--out")
    a = ap.parse_args()
    main_local(a.acts, a.directions, a.out) if a.acts else main()
