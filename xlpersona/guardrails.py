from contextlib import nullcontext

from . import baselines
from .hooks import ablate_spec, cap_spec

GUARDRAILS = [
    "base",
    "cap_en_q95", "cap_en_q99", "cap_en_q999",
    "cap_own_q99", "cap_pooled_q99", "cap_rand_q99",
    "ablate_en", "ablate_pooled", "ablate_rand",
    "anchor_0.5", "anchor_1", "anchor_2",
    "caa_1",
]
Q = {"q95": 0.95, "q99": 0.99, "q999": 0.999}


def _key(k, cond):
    return cond if k == "own" else k


def _caa_layer(model, D):
    try:
        return baselines._caa_layer(model)
    except Exception:
        return D["lstar"]


def make(name, cond, D, hook, model, tok, prompts=None):
    parts = name.split("_")
    if name == "base":
        return nullcontext()
    if parts[0] == "cap":
        k = _key(parts[1], cond)
        return hook.apply(cap_spec(D["unit"][k], D["tau"][k][Q[parts[2]]], D["window"]))
    if parts[0] == "ablate":
        k = _key(parts[1], cond)
        return hook.apply(ablate_spec(D["unit"][k][D["lstar"]], hook.L))
    if tok is None or prompts is None:
        tok, prompts = None, {"harmful": [], "benign": [], "persona": [], "plain": []}
    if parts[0] == "anchor":
        layer = D["lstar"]
        return baselines.refusal_anchor(model, tok, prompts["harmful"], prompts["benign"], float(parts[1]),
                                        fallback=(hook, D["refusal_diff"][layer], layer), calib=D.get("anchor"))
    if parts[0] == "caa":
        layer = _caa_layer(model, D)
        return baselines.caa(model, tok, prompts["plain"], prompts["persona"], float(parts[1]),
                             fallback=(hook, D["diff"]["en"][layer], layer))
    raise ValueError(name)
