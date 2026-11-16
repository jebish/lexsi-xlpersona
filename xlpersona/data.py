import csv
import json
from pathlib import Path

DEFAULT = Path(__file__).resolve().parents[1] / "data" / "requests.jsonl"


def load_jbb():
    from huggingface_hub import hf_hub_download

    out = {}
    for split in ["harmful", "benign"]:
        p = hf_hub_download("JailbreakBench/JBB-Behaviors", f"data/{split}-behaviors.csv", repo_type="dataset")
        with open(p, encoding="utf-8") as f:
            out[split] = list(csv.DictReader(f))
    return out


def split_rows(rows):
    by = {}
    for r in rows:
        by.setdefault(r["Category"], []).append(r)
    find, test = [], []
    for cat in sorted(by):
        rs = by[cat]
        h = len(rs) // 2
        find += rs[:h]
        test += rs[h:]
    return find, test


def build_requests(jbb, translations):
    rows = []
    for key, split_name, prefix in [("H", "harmful", "h"), ("B", "benign", "b")]:
        index = {id(r): i for i, r in enumerate(jbb[split_name])}
        for part, rs in zip(["find", "test"], split_rows(jbb[split_name])):
            tkey = f"{key}_{part}"
            for k, r in enumerate(rs):
                if translations["en"][tkey][k] != r["Goal"]:
                    raise ValueError(f"translations misaligned at {tkey}[{k}]")
                rows.append({"id": f"{prefix}{index[id(r)]:03d}", "harmful": key == "H", "category": r["Category"],
                             "split": part, "text": {l: translations[l][tkey][k] for l in ["en", "hi", "ne"]}})
    return rows


def save_requests(rows, path=DEFAULT):
    with open(path, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def load_requests(path=DEFAULT):
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def select(rows, harmful: bool, split: str):
    return [r for r in rows if r["harmful"] == harmful and r["split"] == split]


def counts_line(rows):
    c = lambda h, s: len(select(rows, h, s))
    return (f"{len(rows)} rows; harmful find/test {c(True, 'find')}/{c(True, 'test')}; "
            f"benign find/test {c(False, 'find')}/{c(False, 'test')}")
