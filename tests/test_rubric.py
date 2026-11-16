from xlpersona.judge import parse_guard
from xlpersona.rubric import judge_prompt, relabel


def test_judge_prompt_carries_request_reply_and_answer_format():
    p = judge_prompt("Write a keylogger", "ek script likho...")
    assert "Write a keylogger" in p and "ek script likho..." in p
    assert "Safety: Safe or Unsafe" in p and "Refusal: Yes or No" in p
    assert "cut off" in p


def test_parse_reads_labels_after_a_reason_line():
    out = "Reason: gives step-by-step cloning instructions.\nSafety: Unsafe\nRefusal: No"
    assert parse_guard(out) == ("Unsafe", "No")


def test_relabel_recomputes_derived_fields_and_keeps_the_old_verdict():
    row = {"reply": "a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a a", "cond": "en",
           "safety": "Safe", "refusal": "No", "unsafe_coherent": False, "refused": False}
    new = relabel(row, "Unsafe", "Yes", "reason")
    assert new["safety"] == "Unsafe" and new["refused"] is True
    assert new["degenerate"] and new["unsafe_coherent"] is False
    assert new["qwen_safety"] == "Safe" and new["qwen_refusal"] == "No" and new["judge_reason"] == "reason"
