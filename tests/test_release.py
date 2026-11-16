import json

from release import build_release_tables


def test_release_has_no_generations(rows, templates, tmp_path):
    out = tmp_path / "main"
    (out / "hi").mkdir(parents=True)
    rec = {"id": "h050", "template": "t4", "cond": "hi", "guardrail": "base", "prompt": "p", "reply": "x" * 5000,
           "raw": "y", "safety": "Unsafe", "refusal": "No", "degenerate": False, "plausible": True,
           "unsafe_coherent": True, "refused": False}
    (out / "hi" / "persona_test__base.jsonl").write_text(json.dumps(rec) + "\n", encoding="utf-8")
    for r in rows:
        r["category"] = "c"
    t = build_release_tables(rows, templates, out, {"cells": {}})
    assert set(t) == {"prompts", "labels", "results"}
    longest = max(len(p["prompt"]) for p in t["prompts"])
    for name in ("prompts", "labels"):
        for row in t[name]:
            assert not {"reply", "raw"} & set(row)
            assert all(len(v) <= longest for v in row.values() if isinstance(v, str))
    assert t["labels"] == [{"id": "h050", "cond": "hi", "guardrail": "base", "set": "persona_test", "template": "t4",
                            "safety": "Unsafe", "refusal": "No",
                            "unsafe_coherent": True, "refused": False, "degenerate": False, "plausible": True}]
    assert {p["cond"] for p in t["prompts"]} >= {"en", "hi", "ne_cm"}
    assert any(p["template"] for p in t["prompts"]) and any(p["template"] is None for p in t["prompts"])


def test_dataset_card_is_minimal():
    from release import dataset_card

    card = dataset_card({"prompts": [1, 2], "labels": [1]})
    assert "config_name: prompts" in card and "config_name: labels" in card
    assert "2 prompts" in card and "1 rows" not in card and "1 labels" in card
    assert "github.com/jebish/lexsi-xlpersona" in card
    for word in ("withheld", "kappa", "Research use", "review", "not released"):
        assert word not in card
