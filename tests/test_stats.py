from xlpersona.stats import auroc, bootstrap_ci, cohen_kappa, mcnemar_exact


def test_mcnemar_matches_known_values():
    base = [True] * 27 + [False] * 10
    treat = [False] * 24 + [True] * 3 + [True] * 3 + [False] * 7
    out = mcnemar_exact(base, treat)
    assert (out["fixed"], out["broke"]) == (24, 3) and out["p"] < 1e-4


def test_mcnemar_no_discordant_pairs():
    assert mcnemar_exact([True, False], [True, False])["p"] == 1.0


def test_auroc_and_kappa():
    assert auroc([2, 3], [0, 1]) == 1.0 and auroc([1], [1]) == 0.5
    assert cohen_kappa(list("SSUU"), list("SSUU")) == 1.0 and cohen_kappa(list("SUSU"), list("USUS")) == -1.0


def test_bootstrap_ci_brackets_mean():
    lo, hi = bootstrap_ci([True] * 40 + [False] * 60)
    assert lo < 0.4 < hi and 0.25 < lo and hi < 0.55
