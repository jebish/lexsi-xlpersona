import argparse
import json
from pathlib import Path

LANGS = ["en", "hi", "ne"]


def pick_top(rates, k=4):
    mean = {t: sum(v[l] for l in LANGS) / len(LANGS) for t, v in rates.items()}
    return sorted(mean, key=lambda t: (-mean[t], t))[:k]


def apply_selection(sel_path, templates_path=None):
    from xlpersona.templates import DEFAULT, load_templates, save_templates

    path = templates_path or DEFAULT
    kept = set(json.loads(Path(sel_path).read_text(encoding="utf-8"))["kept"])
    ts = load_templates(path)
    for t in ts.values():
        if t.split == "heldout":
            t.kept = t.id in kept
    save_templates(ts, path)


def run(smoke):
    import torch

    from xlpersona.data import load_requests, select
    from xlpersona.io import OUT, log, write_json, write_jsonl
    from xlpersona.judge import Guard, label
    from xlpersona.model import generate, load
    from xlpersona.templates import heldout_ids, load_templates, wrap

    dev = "cuda" if torch.cuda.is_available() else "cpu"
    ts = load_templates()
    reqs = select(load_requests(), True, "find")[: 4 if smoke else None]
    cands = heldout_ids(ts, kept_only=False)
    rows = [{"id": r["id"], "template": t, "cond": l, "prompt": wrap(ts[t], l, r["text"][l])}
            for t in cands for l in LANGS for r in reqs]
    tok, model = load(device=dev, smoke=smoke)
    log("generating", len(rows))
    replies = generate(tok, model, [r["prompt"] for r in rows], max_new=16 if smoke else 160)
    del model
    torch.cuda.empty_cache() if dev == "cuda" else None
    for r, rep in zip(rows, replies):
        r["reply"] = rep
    log("judging")
    for r, j in zip(rows, Guard(dev, smoke=smoke)(rows)):
        r.update(safety=j["safety"], refusal=j["refusal"])
    rows = [label(r) for r in rows]
    rates = {t: {l: sum(r["unsafe_coherent"] for r in rows if r["template"] == t and r["cond"] == l) / len(reqs)
                 for l in LANGS} for t in cands}
    kept = pick_top(rates)
    write_jsonl(rows, OUT / "heldout" / "generations.jsonl")
    res = {"rates": rates, "kept": kept, "n_per_cell": len(reqs),
           "kept_mean": sum(sum(rates[t].values()) / 3 for t in kept) / len(kept)}
    write_json(res, OUT / "heldout_selection.json")
    print(f"{'template':20s} " + " ".join(f"{l:>6s}" for l in LANGS))
    for t in cands:
        print(f"{t:20s} " + " ".join(f"{rates[t][l]:6.2f}" for l in LANGS) + ("  KEPT" if t in kept else ""))
    print("kept mean unsafe_coherent:", round(res["kept_mean"], 3))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--apply")
    a = ap.parse_args()
    if a.apply:
        apply_selection(a.apply)
        print("applied", a.apply)
    else:
        run(a.smoke)


if __name__ == "__main__":
    main()
