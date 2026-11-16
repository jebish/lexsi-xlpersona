import argparse

import torch

from xlpersona import baselines
from xlpersona.conditions import CONDITIONS
from xlpersona.data import load_requests
from xlpersona.directions import (choose_layer, diff_in_means, neuron_effect, random_units, split_half_sep,
                                  top_neurons, unit, window)
from xlpersona.hooks import ProjSink, Resid
from xlpersona.io import OUT, log, write_json, write_jsonl
from xlpersona.model import MODEL, chat_text, generate, last_resid, load, mlp_last, sink_pass
from xlpersona.prompts import stage1_prompt_sets
from xlpersona.templates import load_templates

QS = (0.95, 0.99, 0.999)


def smoke_data(rows, ts, k=4):
    from xlpersona.conditions import LANG

    out = []
    for h in (True, False):
        for s in ("find", "test"):
            out += [r for r in rows if r["harmful"] == h and r["split"] == s][:k]
    for r in out:
        for c in CONDITIONS:
            r["text"].setdefault(c, r["text"][LANG[c]])
    held = [t for t in ts.values() if t.split == "heldout"]
    if not any(t.kept for t in held):
        for t in held[:4]:
            t.kept = True
    for t in ts.values():
        for c in CONDITIONS:
            t.text.setdefault(c, t.text[LANG[c]])
    return out, ts


def out_dir(smoke):
    return OUT / ("main_smoke" if smoke else "main")


def main(smoke):
    out = out_dir(smoke)
    tok, model = load(device="cuda", smoke=smoke)
    hook = Resid(model)
    L, d = hook.L, model.config.hidden_size
    rows, ts = load_requests(), load_templates()
    if smoke:
        rows, ts = smoke_data(rows, ts)
    prompts = stage1_prompt_sets(rows, ts)
    plain = [p for p in prompts if p.template is None]
    persona = [p for p in prompts if p.template]
    max_new = 16 if smoke else 160

    acts = {}
    for c in CONDITIONS:
        P = last_resid(tok, model, hook, [p.text for p in persona if p.cond == c])
        Q = last_resid(tok, model, hook, [p.text for p in plain if p.cond == c and p.harmful])
        acts[c] = (P, Q)
        log(c, "persona", tuple(P.shape), "plain", tuple(Q.shape))
    diff = {c: diff_in_means(*acts[c]) for c in CONDITIONS}
    diff["pooled"] = torch.stack([diff[c] for c in CONDITIONS]).mean(0)
    units = {k: unit(v) for k, v in diff.items()}
    units["rand"] = random_units(L, d, seed=0)
    sep = {c: split_half_sep(*acts[c]).tolist() for c in CONDITIONS}
    lstar = choose_layer(torch.tensor(sep["en"]))
    win = window(lstar, L)
    cos = {c: round(float(units[c][lstar] @ units["en"][lstar]), 4) for c in CONDITIONS}
    log("lstar", lstar, "window", win)
    log("cos to en at lstar", cos)

    en_h = [p.text for p in plain if p.cond == "en" and p.harmful]
    en_b = [p.text for p in plain if p.cond == "en" and not p.harmful]
    refusal_diff = diff_in_means(acts["en"][1], last_resid(tok, model, hook, en_b))
    try:
        anchor = baselines.anchor_calibration(model, tok, en_h, en_b)
        anchor_impl = "safetune"
    except Exception as e:
        log(f"SafeTune anchor calibration failed: {type(e).__name__}: {e}")
        anchor, anchor_impl = None, f"fallback ({type(e).__name__})"

    log("reference traffic: generating", len(plain))
    replies = generate(tok, model, [p.text for p in plain], max_new=max_new)
    write_jsonl([{"id": p.id, "cond": p.cond, "harmful": p.harmful, "reply": r} for p, r in zip(plain, replies)],
                out / "reference_generations.jsonl")
    keys = list(CONDITIONS) + ["pooled", "rand"]
    sink = ProjSink({l: torch.stack([units[k][l] for k in keys]) for l in win})
    sink_pass(tok, model, hook, [chat_text(tok, p.text, reply=r) for p, r in zip(plain, replies)], sink)
    tau = {k: {q: {} for q in QS} for k in keys}
    for q in QS:
        qv = sink.quantile(q)
        for i, k in enumerate(keys):
            for l in win:
                tau[k][q][l] = float(qv[l][i])
    log("tau en q99", {l: round(v, 2) for l, v in tau["en"][0.99].items()})

    neurons = {}
    for c in CONDITIONS:
        Pm = mlp_last(tok, model, [p.text for p in persona if p.cond == c])
        Qm = mlp_last(tok, model, [p.text for p in plain if p.cond == c and p.harmful])
        neurons[c] = sorted(top_neurons(neuron_effect(Pm, Qm), 500))
        del Pm, Qm

    D = {"diff": diff, "unit": units, "tau": tau, "lstar": lstar, "window": win, "refusal_diff": refusal_diff,
         "anchor": anchor, "L": L, "d": d}
    out.mkdir(parents=True, exist_ok=True)
    torch.save(D, out / "directions.pt")
    write_json({"model": MODEL, "smoke": smoke, "lstar": lstar, "window": win, "sep": sep, "cos_to_en": cos,
                "n_persona_per_cond": len(persona) // len(CONDITIONS), "n_plain_per_cond": len(plain) // len(CONDITIONS),
                "anchor_impl": anchor_impl,
                "anchor_layer": anchor["layer"] if anchor else None, "anchor_norm": anchor["norm"] if anchor else None,
                "refusal_diff_norm_lstar": float(refusal_diff[lstar].norm()),
                "n_neurons": L * model.config.intermediate_size,
                "cos_matrix": [[round(float(units[a][lstar] @ units[b][lstar]), 4) for b in CONDITIONS]
                               for a in CONDITIONS],
                "diff_norm_lstar": {k: float(v[lstar].norm()) for k, v in diff.items()}}, out / "meta.json")
    write_json({c: [list(x) for x in v] for c, v in neurons.items()}, out / "neuron_sets.json")
    log("stage 1 done ->", out)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true")
    main(ap.parse_args().smoke)
