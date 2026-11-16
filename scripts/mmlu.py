import argparse

import torch

from stage1 import out_dir, smoke_data
from stage2 import kit_prompts
from xlpersona import baselines
from xlpersona.capability import evaluate_mmlu, load_global_mmlu
from xlpersona.data import load_requests
from xlpersona.guardrails import make
from xlpersona.hooks import Resid
from xlpersona.io import OUT, log, write_json
from xlpersona.model import generate, load
from xlpersona.templates import load_templates

GUARDS = ["base", "cap_en_q99", "cap_rand_q99", "ablate_en", "anchor_1", "caa_1"]
LANGS = ["en", "hi", "ne"]


def main(smoke):
    n = 10 if smoke else 200
    tok, model = load(device="cuda", smoke=smoke)
    hook = Resid(model)
    D = torch.load(out_dir(smoke) / "directions.pt", weights_only=False)
    rows, ts = load_requests(), load_templates()
    if smoke:
        rows, ts = smoke_data(rows, ts)
    kp = kit_prompts(rows, ts)
    items = {l: load_global_mmlu(l, n) for l in LANGS}
    res = {}
    for g in GUARDS:
        for l in LANGS:
            with make(g, l, D, hook, model, tok, kp):
                r = evaluate_mmlu(lambda ps: generate(tok, model, ps, max_new=16), l, n, items=items[l])
            res.setdefault(g, {})[l] = r
            log(g, l, r)
    write_json({"n": n, "results": res, "impl": baselines.IMPL}, OUT / ("mmlu_smoke.json" if smoke else "mmlu.json"))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true")
    main(ap.parse_args().smoke)
