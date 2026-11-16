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


def test_dataset_card_reports_final_judge_agreement_and_prompt_review():
    from release import dataset_card

    tables = {"prompts": [1, 2], "labels": [1]}
    judge = {"safety": {"native": {"cohen_kappa": 0.6154}, "rom": {"cohen_kappa": 0.2}}}
    review = {"item/ne_cm/random": {"n": 20, "wrong": 14}, "item/hi_rom/random": {"n": 20, "wrong": 0}}
    card = dataset_card(tables, {"generator": "g"}, judge, review)
    assert "native 0.615" in card and "rom 0.200" in card
    assert "ne_cm 14/20" in card and "hi_rom 0/20" in card
    assert "by hand" not in card and "pending" not in card and "not completed" not in card
