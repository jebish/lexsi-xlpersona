import argparse
import csv
import json
from pathlib import Path

LOW_COMPREHENSION = 14 / 20


def _rows(path):
    with open(path, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def apply_review(csv_path, requests_path=None, templates_path=None) -> dict:
    from xlpersona.data import DEFAULT as REQ, load_requests, save_requests
    from xlpersona.templates import DEFAULT as TPL, load_templates, save_templates

    requests_path, templates_path = requests_path or REQ, templates_path or TPL
    reqs = {r["id"]: r for r in load_requests(requests_path)}
    ts = load_templates(templates_path)
    rep = {"item": {}, "template": {}}
    for line in _rows(csv_path):
        ok = line["ok"].strip().upper()[:1]
        if ok not in ("Y", "N"):
            continue
        kind, i, cond, fix = line["kind"], line["id"], line["cond"], line["fix"].strip()
        cell = rep[kind].setdefault(cond, {"n": 0, "errors": 0})
        cell["n"] += 1
        if ok == "N":
            cell["errors"] += 1
            if fix and kind == "item":
                reqs[i]["text"][cond] = fix
                reqs[i].setdefault("meta", {}).setdefault(cond, {})["source"] = "manual_review"
            elif fix and kind == "template":
                if fix.count("{request}") != 1:
                    raise ValueError(f"template fix for {i}/{cond} must contain exactly one {{request}}")
                ts[i].text[cond] = fix
    for part in rep.values():
        for cell in part.values():
            cell["error_rate"] = cell["errors"] / cell["n"]
    save_requests(list(reqs.values()), requests_path)
    save_templates(ts, templates_path)
    return rep


def comprehension(csv_path) -> dict:
    out = {}
    for line in _rows(csv_path):
        s = line["sensible"].strip().upper()[:1]
        if s in ("Y", "N"):
            c = out.setdefault(line["cond"], {"n": 0, "sensible": 0})
            c["n"] += 1
            c["sensible"] += s == "Y"
    for c in out.values():
        c["score"] = c["sensible"] / c["n"]
        c["low_comprehension"] = c["score"] < LOW_COMPREHENSION
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("review")
    ap.add_argument("--comprehension", default="labels/comprehension.csv")
    a = ap.parse_args()
    rep = {"review": apply_review(a.review)}
    if Path(a.comprehension).exists():
        rep["comprehension"] = comprehension(a.comprehension)
    Path("results").mkdir(exist_ok=True)
    Path("results/validation_report.json").write_text(json.dumps(rep, indent=1, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(rep, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
