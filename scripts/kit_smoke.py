import torch

from xlpersona import baselines
from xlpersona.capability import evaluate_mmlu
from xlpersona.data import load_requests, select
from xlpersona.hooks import Resid
from xlpersona.io import OUT, log, write_json
from xlpersona.model import generate, load
from xlpersona.templates import find_ids, load_templates, wrap


def main():
    tok, model = load(device="cuda")
    rows = load_requests()
    harm = [r["text"]["en"] for r in select(rows, True, "find")]
    benign = [r["text"]["en"] for r in select(rows, False, "find")]
    test = [r["text"]["en"] for r in select(rows, True, "test")][:5]
    ts = load_templates()
    persona = [wrap(ts[find_ids(ts)[i % 4]], "en", h) for i, h in enumerate(harm)]

    hook = Resid(model)
    layer = int(0.4 * hook.L)
    fb_anchor = (hook, baselines._mean_last(model, tok, harm, layer) - baselines._mean_last(model, tok, benign, layer), layer)
    fb_caa = (hook, baselines._mean_last(model, tok, persona, layer) - baselines._mean_last(model, tok, harm, layer), layer)

    base = generate(tok, model, test, max_new=80)
    with baselines.refusal_anchor(model, tok, harm, benign, 1.0, fallback=fb_anchor):
        anchored = generate(tok, model, test, max_new=80)
    changed = sum(a.strip() != b.strip() for a, b in zip(base, anchored))
    log(f"(a) anchor s=1 changed {changed}/5 replies; IMPL={baselines.IMPL}; META={baselines.META.get('anchor')}")
    with baselines.caa(model, tok, harm, persona, 1.0, fallback=fb_caa):
        steered = generate(tok, model, [persona[0]], max_new=40)
    log(f"(b) caa ran; IMPL={baselines.IMPL}; META={baselines.META.get('caa')}")

    gen_fn = lambda prompts: generate(tok, model, prompts, max_new=16)
    mmlu = evaluate_mmlu(gen_fn, "en", n=10)
    log(f"(c) mmlu en n=10: {mmlu}")
    ok = changed >= 3 and 0 <= mmlu["acc"] <= 1 and mmlu["unparsed"] <= 2
    write_json({"anchor_changed": changed, "impl": baselines.IMPL, "meta": baselines.META,
                "mmlu": mmlu, "caa_reply_len": len(steered[0]), "ok": ok}, OUT / "kit_smoke.json")
    print("KIT SMOKE", "PASS" if ok else "FAIL")
    torch.cuda.empty_cache()


if __name__ == "__main__":
    main()
