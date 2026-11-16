from xlpersona.capability import extract_letter, mmlu_prompt


def test_extract_letter():
    assert extract_letter("The answer is (C).") == "C" and extract_letter("उत्तर: B") == "B" and extract_letter("none") is None


def test_extract_letter_ignores_words():
    assert extract_letter("A good question. The answer is D") == "D"
    assert extract_letter("D") == "D" and extract_letter("**B**") == "B"


def test_mmlu_prompt_lists_choices():
    item = {"question": "2+2?", "choices": ["3", "4", "5", "6"], "answer": "B"}
    p = mmlu_prompt(item, "hi")
    assert "A. 3" in p and "D. 6" in p and "2+2?" in p and "उत्तर" in p
