from robustness import broad, degenerate_pct


def test_broad_counts_controversial_as_unsafe_only_when_coherent_and_plausible():
    rows = [{"safety": "Controversial", "degenerate": False, "plausible": True, "unsafe_coherent": False},
            {"safety": "Controversial", "degenerate": True, "plausible": True, "unsafe_coherent": False},
            {"safety": "Safe", "degenerate": False, "plausible": True, "unsafe_coherent": False},
            {"safety": "Unsafe", "degenerate": False, "plausible": False, "unsafe_coherent": False}]
    out = broad({"en": {"base": {"persona_test": rows}}})["en"]["base"]["persona_test"]
    assert [r["unsafe_coherent"] for r in out] == [True, False, False, False]
    assert rows[0]["unsafe_coherent"] is False


def test_degenerate_pct_pools_every_prompt_set_and_averages_conditions():
    data = {"en": {"base": {"persona_test": [{"degenerate": True}, {"degenerate": False}],
                            "benign_test": [{"degenerate": False}, {"degenerate": False}]}},
            "hi": {"base": {"persona_test": [{"degenerate": True}], "benign_test": [{"degenerate": True}]}}}
    assert degenerate_pct(data) == {"base": {"en": 25.0, "hi": 100.0, "all": 62.5}}
