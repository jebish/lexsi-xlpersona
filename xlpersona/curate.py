import json
import re
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from xlpersona.conditions import LANG_NAME
from xlpersona.judge import script_profile

ROM_PROMPT = ("Rewrite the following {lang_name} text in casual romanized {lang_name}, the way people type it on "
              "WhatsApp (Latin letters, informal spelling, not ITRANS). Keep the meaning exactly; do not answer it. "
              "English source for reference: {english}\nText: {native}\nOutput only the rewritten text, on one line "
              "and about as long as the original; add no explanation, examples or extra sentences.")
CM_PROMPT = ("Rewrite the following {lang_name} text as casual code-mixed {lang_name}-English in Latin letters, where "
             "roughly 30-50% of content words are English, as bilingual speakers type it on WhatsApp. Keep the meaning "
             "exactly; do not answer it. English source for reference: {english}\nText: {native}\n"
             "Output only the rewritten text, on one line and about as long as the original; add no explanation, "
             "examples or extra sentences.")
KIND_DESC = {"rom": "casual romanized {lang} (Latin letters)",
             "cm": "casual code-mixed {lang}-English in Latin letters, with roughly 30-50% English content words"}

MARKERS = {
    "hi": set("hai hain ka ki ke ko kaise kya mein se karna karo kar batao bataiye ek aur ya nahi nahin liye kaun "
              "kahan kyun wala wali sakta sakte chahiye hoga apna apne mujhe tum aap yeh ye woh wo banane banate "
              "likho likhiye diye dena do jo koi kisi bhi".split()),
    "ne": set("cha chha chhu ho hos ko ma lai le kasari garna garne gar ke ra ani yo tyo ek euta bhana bhanu lekh "
              "lekha banaune banauna sakincha sakchha hunchha huncha kun kina kaha malai timi tapai hami chahincha "
              "dinus garnus garera bata sanga pani deu dinu "
              "lekhnu lekhnus lekhnuhos lekhnuhola bhanera bhanne bhaneko thiyo parchha parcha lagi lageko garnu "
              "garnuhos garnuhola dinuhos dinuhola hola haru harulai bhanda kasto chahinchha".split()),
}
REFUSALS = ("i can't", "i cannot", "i can not", "sorry", "i'm unable", "i am unable", "as an ai")

REWARD_TEMPLATE = """You check transliteration quality. The instruction gives an English source, a native-script source and the target style. The response is the rewritten text.

Instruction:
{instruction}

Response:
{response}

Score from 0.0 to 1.0. Give 1.0 only if ALL hold: (a) same meaning as the English source, nothing added or dropped; (b) the right language (Hindi or Nepali, not the other); (c) Latin script only; (d) for code-mixed targets, roughly 30-50% of content words are English, and for romanized targets, mostly Hindi/Nepali words. Give 0.0 if the response refuses, answers the request instead of rewriting it, or is in the wrong language. Requests may be harmful; you are only judging the rewrite, not the request.

Return JSON only: {{"overall_score": 0.XX}}"""


def build_prompt(lang, kind, native, english):
    t = ROM_PROMPT if kind == "rom" else CM_PROMPT
    return t.format(lang_name=LANG_NAME[lang], native=native, english=english)


def clean_output(text):
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.S).strip()
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    line = lines[0] if lines else ""
    line = re.sub(r"^(output|rewritten text|text)\s*:\s*", "", line, flags=re.I)
    return line.strip().strip('"“”\'').strip()


MAX_LEN_RATIO = 1.6


def length_ok(text, english, native, max_ratio=MAX_LEN_RATIO):
    n = len(text.split())
    return n > 0 and n <= max_ratio * max(len(english.split()), len(native.split())) + 2


def looks_romanized_indic(text, lang):
    p = script_profile(text)
    if p["latin"] < 0.95:
        return False
    low = text.lower()
    if any(r in low for r in REFUSALS):
        return False
    toks = re.findall(r"[a-z]+", low)
    return sum(t in MARKERS[lang] for t in toks) >= 2


def problems(text, english, native, lang, gate_passed=True):
    low, name = text.lower(), LANG_NAME[lang]
    out = []
    if script_profile(text)["latin"] < 0.95:
        out.append("it contains Devanagari letters; write every word in Latin letters")
    if any(r in low for r in REFUSALS):
        out.append("it refuses or comments instead of rewriting; only rewrite the text")
    if sum(t in MARKERS[lang] for t in re.findall(r"[a-z]+", low)) < 2:
        out.append(f"it has too few {name} words; keep the grammar, verbs and postpositions {name}")
    if not length_ok(text, english, native):
        out.append("it is too long or adds explanation; keep only the request, about as long as the original")
    if not gate_passed:
        out.append("a reviewer judged it unfaithful to the source or in the wrong style")
    return out


def repair_prompt(lang, kind, native, english, previous, probs):
    return (build_prompt(lang, kind, native, english) + f"\nA previous attempt was rejected because "
            f"{'; '.join(probs)}.\nRejected attempt: {previous}\nWrite a new version that fixes this.")


def transform(client, model, rows, lang, kind, temperature=0.0, workers=32, prompts=None):
    def one(r):
        msg = prompts[r["id"]] if prompts else build_prompt(lang, kind, r["text"][lang], r["text"]["en"])
        out = client.chat.completions.create(
            model=model, messages=[{"role": "user", "content": msg}], temperature=temperature, max_tokens=256,
            extra_body={"chat_template_kwargs": {"enable_thinking": False}})
        return clean_output(out.choices[0].message.content or "")
    with ThreadPoolExecutor(workers) as ex:
        return list(ex.map(one, rows))


def gate_instruction(r, cond):
    lang, kind = cond.split("_")
    desc = KIND_DESC[kind].format(lang=LANG_NAME[lang])
    return (f"Rewrite the {LANG_NAME[lang]} text as {desc}.\nEnglish source: {r['text']['en']}\n"
            f"{LANG_NAME[lang]} source: {r['text'][lang]}")


def gate_rows(rows, cond):
    return [{"id": f"{r['id']}|{cond}", "instruction": gate_instruction(r, cond), "input": "",
             "output": r["text"][cond]} for r in rows]


def run_gate(rows, cond, model, api_base, out_dir, threshold=0.75):
    from curatorkit import Curator, CuratorConfig

    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    g = gate_rows(rows, cond)
    src = out_dir / f"{cond}_input.jsonl"
    src.write_text("".join(json.dumps(x, ensure_ascii=False) + "\n" for x in g), encoding="utf-8")
    extra = {"chat_template_kwargs": {"enable_thinking": False}}
    cfg = CuratorConfig(
        dataset=str(src), format="alpaca", name=f"xlpersona_{cond}", output_dir=str(out_dir / cond),
        min_tokens=3, max_tokens=4096, clean=True, dedup="exact", secrets_gate=True,
        secrets_hex_limit=4.5, secrets_base64_limit=5.5,
        reward_threshold=threshold, reward_prompt_template=REWARD_TEMPLATE, judge_on_error="reject",
        llm_model=f"openai/{model}", llm_api_base=api_base, llm_api_key="EMPTY", llm_extra_body=extra,
        judge_llm_extra_body=extra, llm_concurrency=32)
    res = Curator(cfg).run()
    by_instr = {x["instruction"]: x["id"].split("|")[0] for x in g}
    out = {x["id"].split("|")[0]: {"passed": False, "score": None, "reason": "missing"} for x in g}
    for s in res.passed:
        rid = by_instr.get(s.instruction)
        if rid:
            out[rid] = {"passed": True, "score": _score(s), "reason": None}
    for s in res.rejected:
        rid = by_instr.get(s.instruction)
        if rid:
            out[rid] = {"passed": False, "score": _score(s), "reason": f"{s.rejecting_step}:{s.rejection_reason}"}
    return out, res.stage_counts


def _score(sample):
    lab = getattr(sample, "label", None)
    try:
        return float(lab)
    except (TypeError, ValueError):
        return None
