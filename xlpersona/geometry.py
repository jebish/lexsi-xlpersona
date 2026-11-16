import math

import torch

from .directions import unit


def _dir(P, Q):
    return unit(P.float().mean(0) - Q.float().mean(0))


def _n(P, Q):
    n_req = Q.shape[0]
    assert P.shape[0] % n_req == 0, "persona rows must be n_tmpl x n_req"
    return n_req, P.shape[0] // n_req


def persona_rows(req_idx, n_req, n_tmpl):
    return torch.cat([t * n_req + req_idx for t in range(n_tmpl)])


def reliability(P, Q, n_splits=100, seed=0):
    n_req, n_tmpl = _n(P, Q)
    g = torch.Generator().manual_seed(seed)
    rs = []
    for _ in range(n_splits):
        r = torch.randperm(n_req, generator=g)
        a, b = r[: n_req // 2], r[n_req // 2:]
        da = _dir(P[persona_rows(a, n_req, n_tmpl)], Q[a])
        db = _dir(P[persona_rows(b, n_req, n_tmpl)], Q[b])
        rs.append(float(da @ db))
    r = max(sum(rs) / len(rs), 0.0)
    return 2 * r / (1 + r)


def dprime(P, Q, u):
    u = unit(u.float())
    pp, qq = P.float() @ u, Q.float() @ u
    return float((pp.mean() - qq.mean()) / ((pp.var() + qq.var()) / 2 + 1e-6).sqrt())


def transfer_geometry(find, test, ref="en", with_rel=True, rand=None):
    dirs = {c: _dir(*find[c]) for c in find}
    rel = {c: reliability(*find[c]) for c in find} if with_rel else {}
    out = {}
    for c in find:
        d_ref, d_own = dprime(*test[c], dirs[ref]), dprime(*test[c], dirs[c])
        row = {"cos": float(dirs[c] @ dirs[ref]), "d_ref": d_ref, "d_own": d_own, "R": d_ref / d_own}
        if rand is not None:
            row["R_rand"] = dprime(*test[c], rand) / d_own
        if with_rel:
            den = math.sqrt(rel[c] * rel[ref])
            row.update(rel=rel[c], cos_corrected=row["cos"] / den if den > 0 else float("nan"))
        out[c] = row
    return out


def _ci(xs):
    t = torch.tensor(xs)
    return float(t.quantile(0.025)), float(t.quantile(0.975))


def boot_geometry(find, test, ref="en", gaps=(), B=1000, seed=0, rand=None):
    g = torch.Generator().manual_seed(seed)
    metrics = ("cos", "d_ref", "d_own", "R")
    nf, tf = _n(*find[ref])
    nt, tt = _n(*test[ref])
    draws = []
    for _ in range(B):
        rf = torch.randint(nf, (nf,), generator=g)
        rt = torch.randint(nt, (nt,), generator=g)
        f = {c: (P[persona_rows(rf, nf, tf)], Q[rf]) for c, (P, Q) in find.items()}
        t = {c: (P[persona_rows(rt, nt, tt)], Q[rt]) for c, (P, Q) in test.items()}
        draws.append(transfer_geometry(f, t, ref, with_rel=False))
    ci = {c: {m: _ci([d[c][m] for d in draws]) for m in metrics} for c in find}
    gp = {f"{a}-{b}": {m: _ci([d[a][m] - d[b][m] for d in draws]) for m in metrics} for a, b in gaps}
    return {"point": transfer_geometry(find, test, ref, rand=rand), "ci": ci, "gaps": gp, "B": B}
