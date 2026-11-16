import torch

from xlpersona.geometry import boot_geometry, dprime, persona_rows, reliability, transfer_geometry

N_REQ, N_T, D = 40, 4, 64


def _cond(direction, seed, shift=3.0):
    g = torch.Generator().manual_seed(seed)
    P = torch.randn(N_REQ * N_T, D, generator=g) + shift * direction
    Q = torch.randn(N_REQ, D, generator=g)
    return P, Q


def _world():
    e = torch.zeros(D)
    e[0] = 1.0
    o = torch.zeros(D)
    o[1] = 1.0
    find = {"en": _cond(e, 0), "x": _cond(e, 1), "y": _cond(o, 2)}
    test = {"en": _cond(e, 3), "x": _cond(e, 4), "y": _cond(o, 5)}
    return find, test


def test_reliability_is_high_for_a_real_direction_and_low_for_noise():
    e = torch.zeros(D)
    e[0] = 1.0
    assert reliability(*_cond(e, 0)) > 0.75
    assert abs(reliability(*_cond(e, 0, shift=0.0))) < 0.5


def test_dprime_recovers_a_known_shift():
    e = torch.zeros(D)
    e[0] = 1.0
    P, Q = _cond(e, 0, shift=2.0)
    assert 1.5 < dprime(P, Q, e) < 2.5
    assert abs(dprime(P, Q, -e) + dprime(P, Q, e)) < 1e-5


def test_persona_rows_follow_template_major_order():
    assert persona_rows(torch.tensor([1, 3]), n_req=5, n_tmpl=2).tolist() == [1, 3, 6, 8]


def test_transfer_geometry_separates_shared_from_orthogonal_directions():
    find, test = _world()
    t = transfer_geometry(find, test, ref="en")
    assert t["x"]["cos"] > 0.8 and abs(t["y"]["cos"]) < 0.3
    assert t["x"]["R"] > 0.8 and abs(t["y"]["R"]) < 0.3
    assert t["en"]["R"] == 1.0
    assert t["x"]["cos_corrected"] >= t["x"]["cos"]


def test_boot_geometry_gives_cis_and_paired_gaps():
    find, test = _world()
    b = boot_geometry(find, test, ref="en", gaps=[("x", "y")], B=50, seed=0)
    lo, hi = b["ci"]["x"]["R"]
    assert lo <= b["point"]["x"]["R"] <= hi
    glo, ghi = b["gaps"]["x-y"]["R"]
    assert glo > 0.5 and ghi > glo


def test_transfer_geometry_reports_a_random_direction_control():
    find, test = _world()
    r = torch.zeros(D)
    r[5] = 1.0
    t = transfer_geometry(find, test, ref="en", rand=r)
    assert abs(t["x"]["R_rand"]) < 0.3 and t["x"]["R"] > 0.8
