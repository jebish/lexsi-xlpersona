import torch


def unit(v):
    return v / (v.norm(dim=-1, keepdim=True) + 1e-8)


def diff_in_means(persona, plain):
    return persona.float().mean(0) - plain.float().mean(0)


def _halves(n, g):
    p = torch.randperm(n, generator=g)
    return p[: n // 2], p[n // 2:]


def _sep(p, q, u):
    pp, qq = p @ u, q @ u
    return float((pp.mean() - qq.mean()) / ((pp.var() + qq.var()) / 2 + 1e-6).sqrt())


def split_half_sep(persona, plain, seed=0):
    g = torch.Generator().manual_seed(seed)
    pa, pb = _halves(persona.shape[0], g)
    qa, qb = _halves(plain.shape[0], g)
    L = persona.shape[1]
    out = []
    for l in range(L):
        u = unit(persona[pa, l].float().mean(0) - plain[qa, l].float().mean(0))
        out.append(_sep(persona[pb, l].float(), plain[qb, l].float(), u))
    return torch.tensor(out)


def choose_layer(sep):
    L = len(sep)
    cand = range(L // 5, max(L // 5 + 1, int(0.8 * L)))
    return max(cand, key=lambda l: float(sep[l]))


def window(lstar, L, half=4):
    return list(range(max(0, lstar - half), min(L, lstar + half + 1)))


def random_units(L, d, seed=0):
    g = torch.Generator().manual_seed(seed)
    return unit(torch.randn(L, d, generator=g))


def neuron_effect(persona, plain):
    d = persona.float().mean(0) - plain.float().mean(0)
    sd = ((persona.float().var(0) + plain.float().var(0)) / 2 + 1e-4).sqrt()
    return d / sd


def top_neurons(score, k=500):
    L, N = score.shape
    idx = torch.topk(score.abs().flatten(), k).indices.tolist()
    return {(i // N, i % N) for i in idx}


def jaccard(a, b):
    a, b = set(a), set(b)
    return len(a & b) / max(len(a | b), 1)


def jaccard_chance(k, total):
    return k / (2 * total - k)
