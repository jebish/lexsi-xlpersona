import argparse
import json

import torch

from stage1 import out_dir, smoke_data
from xlpersona import baselines
from xlpersona.cells import run_cells
from xlpersona.data import load_requests
from xlpersona.guardrails import GUARDRAILS, make
from xlpersona.hooks import Resid
from xlpersona.io import log, write_json
from xlpersona.judge import Guard, label
from xlpersona.model import generate, last_resid, load
from xlpersona.prompts import stage1_prompt_sets, stage2_prompt_sets
from xlpersona.templates import load_templates

PLAIN_GUARDRAILS = ("base", "cap_en_q99")


def build_cells(sets):
    cells = []
    for g in GUARDRAILS:
        for s in ["persona_test", "benign_test"] + (["plain_test"] if g in PLAIN_GUARDRAILS else []):
            cells.append({"name": f"{s}__{g}", "n": len(sets[s]), "set": s, "guardrail": g})
    return cells


def kit_prompts(rows, ts):
    p1 = [p for p in stage1_prompt_sets(rows, ts) if p.cond == "en"]
    return {"harmful": [p.text for p in p1 if p.template is None and p.harmful],
            "benign": [p.text for p in p1 if p.template is None and not p.harmful],
            "plain": [p.text for p in p1 if p.template is None and p.harmful],
            "persona": [p.text for p in p1 if p.template]}


def main(cond, smoke):
    root = out_dir(smoke)
    out = root / cond
    tok, model = load(device="cuda", smoke=smoke)
    hook = Resid(model)
    D = torch.load(root / "directions.pt", weights_only=False)
    rows, ts = load_requests(), load_templates()
    if smoke:
        rows, ts = smoke_data(rows, ts)
    sets = stage2_prompt_sets(rows, ts, cond)
    kp = kit_prompts(rows, ts)
    guard = Guard("cuda", smoke=smoke)
    max_new = 16 if smoke else 160

    def fn(cell):
        ps = sets[cell["set"]]
        with make(cell["guardrail"], cond, D, hook, model, tok, kp):
            replies = generate(tok, model, [p.text for p in ps], max_new=max_new)
        recs = [{"id": p.id, "template": p.template, "cond": cond, "guardrail": cell["guardrail"],
                 "prompt": p.text, "reply": r} for p, r in zip(ps, replies)]
        for r, j in zip(recs, guard(recs)):
            r.update(safety=j["safety"], refusal=j["refusal"])
        recs = [label(r) for r in recs]
        log(cell["name"], "unsafe_coherent", sum(r["unsafe_coherent"] for r in recs), "/", len(recs),
            "refused", sum(r["refused"] for r in recs), "impl", baselines.IMPL)
        return recs

    run_cells(build_cells(sets), out, fn)

    mon = out / "monitor.json"
    if not mon.exists():
        ps = sets["persona_test"]
        X = last_resid(tok, model, hook, [p.text for p in ps])[:, D["lstar"]]
        U = {"en": D["unit"]["en"], "own": D["unit"][cond], "rand": D["unit"]["rand"]}
        write_json({"lstar": D["lstar"], "ids": [p.id for p in ps], "templates": [p.template for p in ps],
                    "proj": {k: (X @ u[D["lstar"]]).tolist() for k, u in U.items()}}, mon)
    write_json({"impl": baselines.IMPL, "meta": baselines.META}, out / "impl.json")
    log("stage 2 done", cond, json.dumps(baselines.IMPL))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--cond", required=True)
    ap.add_argument("--smoke", action="store_true")
    a = ap.parse_args()
    main(a.cond, a.smoke)
