import csv

from xlpersona.data import load_requests, select
from xlpersona.io import OUT
from xlpersona.model import generate, load

NEW = ["hi_rom", "ne_rom", "hi_cm", "ne_cm"]


def main():
    tok, model = load(device="cuda")
    reqs = select(load_requests(), False, "test")[:5]
    items = [(c, r["text"][c]) for c in NEW for r in reqs]
    replies = generate(tok, model, [t for _, t in items], max_new=200)
    OUT.mkdir(parents=True, exist_ok=True)
    with open(OUT / "comprehension.csv", "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["cond", "request", "reply", "sensible"])
        for (c, t), rep in zip(items, replies):
            w.writerow([c, t, rep, ""])
    print("wrote", OUT / "comprehension.csv", len(items))


if __name__ == "__main__":
    main()
