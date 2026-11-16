import random
import re

ASK = {
    "en": "Answer with only the letter of the correct option (A, B, C or D).",
    "hi": "केवल सही विकल्प का अक्षर (A, B, C या D) लिखकर उत्तर दें।",
    "ne": "सही विकल्पको अक्षर (A, B, C वा D) मात्र लेखेर उत्तर दिनुहोस्।",
}
LETTERS = "ABCD"
_MARKER = re.compile(r"(?i:answer|ans|उत्तर|जवाब|जवाफ|विकल्प)\s*(?:is|:|है|हो|छ|=)?\s*[:\-]?\s*[\(\[\*\s]*([ABCD])(?![A-Za-z])")
_PAREN = re.compile(r"\(([ABCD])\)")
_ALONE = re.compile(r"^\W*([ABCD])\W*$")
_LEAD = re.compile(r"^\W*([ABCD])[\.\):](?!\w)")


def load_global_mmlu(lang, n=200, seed=0):
    from datasets import load_dataset

    ds = load_dataset("CohereLabs/Global-MMLU", lang, split="test")
    idx = sorted(random.Random(seed).sample(range(len(ds)), min(n, len(ds))))
    rows = ds.select(idx)
    return [{"question": r["question"], "answer": r["answer"].strip(), "sample_id": r.get("sample_id"),
             "choices": [r["option_a"], r["option_b"], r["option_c"], r["option_d"]]} for r in rows]


def mmlu_prompt(item, lang):
    opts = "\n".join(f"{LETTERS[i]}. {c}" for i, c in enumerate(item["choices"]))
    return f"{item['question']}\n\n{opts}\n\n{ASK[lang]}"


def extract_letter(reply):
    if not reply:
        return None
    text = reply.strip()
    for pat in (_MARKER, _PAREN, _ALONE, _LEAD):
        m = pat.search(text)
        if m:
            return m.group(1)
    return None


def evaluate_mmlu(gen_fn, lang, n=200, items=None):
    import auditkit as ak
    from auditkit.scorers import FunctionScorer
    from auditkit.types import Direction

    items = items if items is not None else load_global_mmlu(lang, n)
    samples = [ak.Sample(input=mmlu_prompt(it, lang), target=it["answer"], id=f"{lang}-{i}")
               for i, it in enumerate(items)]

    def mmlu_letter_match(sample, output):
        return float(extract_letter(output) == sample.target)

    score = FunctionScorer(mmlu_letter_match, direction=Direction.MAXIMIZE)
    res = ak.evaluate(samples, gen_fn, scorers=score, cache=False)
    by_id = {p.sample_id: p.raw_output for p in res.predictions}
    outs = [by_id.get(s.id) for s in samples]
    acc = sum(float(extract_letter(o) == s.target) for o, s in zip(outs, samples)) / max(1, len(samples))
    return {"acc": acc, "n": len(samples), "unparsed": sum(extract_letter(o) is None for o in outs),
            "auditkit_headline": dict(res.headline)}
