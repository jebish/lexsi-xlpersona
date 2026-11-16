import argparse
import csv
import json
import random
from collections import defaultdict
from pathlib import Path

COLUMNS = ["uid", "cond", "prompt", "reply", "human_safety", "human_refusal"]
LABEL_CONDS = ["hi", "ne", "hi_rom", "ne_rom", "hi_cm", "ne_cm"]
JUDGE = ("Unsafe", "Safe")


def kind(cond):
    return "rom" if cond.endswith("_rom") else "cm" if cond.endswith("_cm") else "native"


def _records(out_dir):
    for cond in LABEL_CONDS:
        for path in sorted((Path(out_dir) / cond).glob("*.jsonl")):
            cell = path.stem.split("__")[0]
            for line in path.read_text(encoding="utf-8").splitlines():
                r = json.loads(line)
                if r["safety"] in JUDGE and not r.get("degenerate") and r.get("plausible", True):
                    yield dict(r, set=cell)


def _interleave(recs, quota, rng):
    groups = defaultdict(list)
    for r in recs:
        groups[r["guardrail"]].append(r)
    order = sorted(groups)
    rng.shuffle(order)
    for g in order:
        rng.shuffle(groups[g])
    picked = []
    while len(picked) < quota and any(groups[g] for g in order):
        for g in order:
            if groups[g] and len(picked) < quota:
                picked.append(groups[g].pop())
    return picked


def export_labels(out_dir, n=150, seed=0, csv_out=Path("labels/judge_sample.csv"),
                  key_out=Path("labels/judge_sample_key.json")):
    rng = random.Random(seed)
    strata = defaultdict(list)
    for r in _records(out_dir):
        strata[(r["cond"], r["safety"])].append(r)
    keys = [(c, s) for c in LABEL_CONDS for s in JUDGE]
    base, extra = divmod(n, len(keys))
    picked = []
    for i, k in enumerate(keys):
        got = _interleave(strata[k], base + (i < extra), rng)
        if len(got) < base + (i < extra):
            print(f"short stratum {k}: {len(got)} of {base + (i < extra)}")
        picked += got
    rng.shuffle(picked)
    rows, key = [], {}
    for i, r in enumerate(picked):
        uid = f"L{i:03d}"
        rows.append({"uid": uid, "cond": r["cond"], "prompt": r["prompt"], "reply": r["reply"],
                     "human_safety": "", "human_refusal": ""})
        key[uid] = {k: r.get(k) for k in ("id", "cond", "guardrail", "set", "safety", "refusal", "degenerate")}
        key[uid]["kind"] = kind(r["cond"])
    Path(csv_out).parent.mkdir(parents=True, exist_ok=True)
    with open(csv_out, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS)
        w.writeheader()
        w.writerows(rows)
    Path(key_out).write_text(json.dumps(key, ensure_ascii=False, indent=1), encoding="utf-8")
    return rows


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("out_dir")
    ap.add_argument("--n", type=int, default=150)
    a = ap.parse_args()
    print(len(export_labels(a.out_dir, a.n)), "rows -> labels/judge_sample.csv")
