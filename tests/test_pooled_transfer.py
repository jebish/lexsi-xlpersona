from pooled_transfer import pooled_transfer


def _rows(flags):
    return [{"id": f"r{i}", "template": t, "unsafe_coherent": f} for i, fl in enumerate(flags) for t, f in enumerate(fl)]


def _data(en_treat, other_treat, n=30):
    base = [[True, True]] * n
    return {
        "en": {"base": {"persona_test": _rows(base)}, "g": {"persona_test": _rows([[en_treat, True]] * n)}},
        "hi": {"base": {"persona_test": _rows(base)}, "g": {"persona_test": _rows([[other_treat, True]] * n)}},
    }


def test_pooled_transfer_reports_reduction_in_pp_and_the_english_gap():
    r = pooled_transfer(_data(en_treat=False, other_treat=True), "g", ref="en", others=["hi"], B=200)
    assert r["ref"]["effect"] == 50.0 and r["others"]["effect"] == 0.0
    assert r["gap"]["effect"] == 50.0 and r["gap"]["ci"][0] > 0


def test_pooled_transfer_gap_is_zero_when_effects_match():
    r = pooled_transfer(_data(en_treat=False, other_treat=False), "g", ref="en", others=["hi"], B=200)
    assert r["gap"]["effect"] == 0.0
