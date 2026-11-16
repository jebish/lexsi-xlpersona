import math
import random


def mcnemar_exact(base, treat):
    fixed = sum(1 for a, b in zip(base, treat) if a and not b)
    broke = sum(1 for a, b in zip(base, treat) if b and not a)
    n = fixed + broke
    if n == 0:
        return {"fixed": 0, "broke": 0, "p": 1.0}
    k = min(fixed, broke)
    p = 2 * sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n
    return {"fixed": fixed, "broke": broke, "p": min(1.0, p)}


def bootstrap_ci(x, n=1000, seed=0):
    x = [float(v) for v in x]
    if not x:
        return (float("nan"), float("nan"))
    rng = random.Random(seed)
    means = sorted(sum(rng.choices(x, k=len(x))) / len(x) for _ in range(n))
    return (means[int(0.025 * n)], means[int(0.975 * n) - 1])


def auroc(pos, neg):
    if not pos or not neg:
        return None
    s = sum(1.0 if a > b else 0.5 if a == b else 0.0 for a in pos for b in neg)
    return s / (len(pos) * len(neg))


def cohen_kappa(a, b):
    n = len(a)
    labels = set(a) | set(b)
    po = sum(x == y for x, y in zip(a, b)) / n
    pe = sum((a.count(c) / n) * (b.count(c) / n) for c in labels)
    if pe == 1:
        return 1.0 if po == 1 else 0.0
    return (po - pe) / (1 - pe)
