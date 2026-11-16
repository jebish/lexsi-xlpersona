import argparse
import json
import random

from analyze import _load

NON_EN = ["hi", "ne", "hi_rom", "ne_rom", "hi_cm", "ne_cm"]
GUARDS = ["cap_en_q95", "cap_en_q99", "cap_own_q99", "cap_pooled_q99", "cap_rand_q99", "ablate_en"]


def _diffs(data, c, g):
    b = {(r["id"], r["template"]): float(r["unsafe_coherent"]) for r in data[c]["base"]["persona_test"]}
    t = {(r["id"], r["template"]): float(r["unsafe_coherent"]) for r in data[c][g]["persona_test"]}
    d = {}
    for k in b:
        if k in t:
            d.setdefault(k[0], []).append(b[k] - t[k])
    return d


def _eff(d, ids):
    xs = [x for i in ids for x in d.get(i, [])]
    return 100 * sum(xs) / len(xs)


def pooled_transfer(data, g, ref="en", others=NON_EN, B=4000, seed=0):
    D = {c: _diffs(data, c, g) for c in [ref] + list(others)}
    ids = sorted(set.intersection(*[set(d) for d in D.values()]))

    def stats(s):
        e = _eff(D[ref], s)
        o = sum(_eff(D[c], s) for c in others) / len(others)
        return {"ref": e, "others": o, "gap": e - o}

    pt, rng = stats(ids), random.Random(seed)
    draws = [stats([rng.choice(ids) for _ in ids]) for _ in range(B)]

    def ci(k):
        v = sorted(d[k] for d in draws)
        return [round(v[int(0.025 * B)], 2), round(v[int(0.975 * B) - 1], 2)]

    return {k: {"effect": round(pt[k], 2), "ci": ci(k)} for k in pt} | {"n_requests": len(ids)}


def main(out_dir, path):
    data = _load(out_dir)
    res = {g: pooled_transfer(data, g) for g in GUARDS}
    with open(path, "w", encoding="utf-8") as f:
        json.dump(res, f, indent=1)
    for g, r in res.items():
        print(g, {k: v for k, v in r.items()})


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("out_dir")
    ap.add_argument("path")
    a = ap.parse_args()
    main(a.out_dir, a.path)
