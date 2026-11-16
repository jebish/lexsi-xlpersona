import argparse
import random

import torch

from xlpersona.data import load_requests
from xlpersona.hooks import Resid, ablate_spec
from xlpersona.io import OUT, log, write_json
from xlpersona.model import generate, load
from xlpersona.orthogonalize import orthogonalize_
from xlpersona.prompts import stage1_prompt_sets
from xlpersona.templates import load_templates

LANGS = ("en", "hi", "ne")
MIN_MATCH = 19


def check_prompts(rows, templates, n=20, seed=0):
    rng = random.Random(seed)
    ps = [p for p in stage1_prompt_sets(rows, templates) if p.template and p.cond in LANGS]
    per = [n // len(LANGS) + (i < n % len(LANGS)) for i in range(len(LANGS))]
    return [p for lang, k in zip(LANGS, per) for p in rng.sample([q for q in ps if q.cond == lang], k)]


def public_directions(D):
    return {"unit": dict(D["unit"]), "diff": dict(D["diff"]), "tau": dict(D["tau"]),
            "lstar": D["lstar"], "window": D["window"]}


def main(smoke):
    root = OUT / ("main_smoke" if smoke else "main")
    dest = OUT / ("ablated_smoke" if smoke else "ablated")
    D = torch.load(root / "directions.pt", weights_only=False)
    r = D["unit"]["en"][D["lstar"]].float()
    tok, model = load(device="cuda", smoke=smoke, dtype=torch.float32)
    rows, ts = load_requests(), load_templates()
    if smoke:
        from stage1 import smoke_data

        rows, ts = smoke_data(rows, ts)
    texts = [p.text for p in check_prompts(rows, ts)]

    base = generate(tok, model, texts, max_new=64)
    hook = Resid(model)
    with hook.apply(ablate_spec(r, hook.L)):
        want = generate(tok, model, texts, max_new=64)
    for h in hook.handles:
        h.remove()
    orthogonalize_(model, r)
    got = generate(tok, model, texts, max_new=64)

    match = sum(a == b for a, b in zip(got, want))
    check = {"n": len(texts), "match": match, "min_match": MIN_MATCH,
             "hook_differs_from_base": sum(a != b for a, b in zip(want, base)), "lstar": D["lstar"]}
    log("orthogonalized vs hook ablation:", match, "/", len(texts), "identical;",
        check["hook_differs_from_base"], "hook generations differ from base")
    for a, b in zip(got, want):
        if a != b:
            log("MISMATCH\n  hook :", b[:200].replace("\n", " "), "\n  ortho:", a[:200].replace("\n", " "))
    if match < MIN_MATCH:
        write_json(check, root / "ablated_check_failed.json")
        raise SystemExit(f"only {match}/{len(texts)} identical (< {MIN_MATCH}); not saving")
    dest.mkdir(parents=True, exist_ok=True)
    model.to(torch.bfloat16)
    model.save_pretrained(dest)
    tok.save_pretrained(dest)
    torch.save(public_directions(D), dest / "directions_public.pt")
    write_json(check, dest / "check.json")
    log("saved", dest)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true")
    main(ap.parse_args().smoke)
