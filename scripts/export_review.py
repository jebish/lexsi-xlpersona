import csv
import random
from pathlib import Path

NEW = ["hi_rom", "ne_rom", "hi_cm", "ne_cm"]
COLS = ["kind", "id", "cond", "english", "native", "variant", "ok", "fix", "note"]


def _flag(row, cond):
    m = row.get("meta", {}).get(cond, {})
    if m.get("source") == "manual":
        return "manual"
    return "gate_failed" if m.get("gate_failed") else ""


def export_review(rows, templates, out: Path = Path("labels/review.csv"), per_cond=20, seed=0) -> Path:
    rng = random.Random(seed)
    lines = []
    for cond in NEW:
        lang = cond.split("_")[0]
        flagged = [r for r in rows if _flag(r, cond)]
        rest = [r for r in rows if not _flag(r, cond) and cond in r["text"]]
        for r in flagged + rng.sample(rest, min(per_cond, len(rest))):
            lines.append({"kind": "item", "id": r["id"], "cond": cond, "english": r["text"]["en"],
                          "native": r["text"][lang], "variant": r["text"].get(cond, ""), "note": _flag(r, cond)})
    for cond in ("hi", "ne"):
        have = [r for r in rows if cond in r["text"]]
        for r in rng.sample(have, min(per_cond, len(have))):
            lines.append({"kind": "item", "id": r["id"], "cond": cond, "english": r["text"]["en"],
                          "native": r["text"][cond], "variant": r["text"][cond], "note": "translation"})
    kept = [t for t in templates.values() if t.split == "find" or t.kept]
    for t in kept:
        conds = (["hi", "ne"] if t.split == "heldout" else []) + NEW
        for cond in conds:
            lang = cond.split("_")[0]
            lines.append({"kind": "template", "id": t.id, "cond": cond, "english": t.text["en"],
                          "native": t.text[lang], "variant": t.text.get(cond, "")})
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLS)
        w.writeheader()
        for line in lines:
            w.writerow({c: line.get(c, "") for c in COLS})
    return out


def main():
    from xlpersona.data import load_requests
    from xlpersona.templates import load_templates

    p = export_review(load_requests(), load_templates())
    print("wrote", p)


if __name__ == "__main__":
    main()
