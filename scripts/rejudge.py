import argparse
import re
from concurrent.futures import ThreadPoolExecutor

from gen_variants import serve
from xlpersona.data import load_requests
from xlpersona.io import OUT, log, read_jsonl, write_jsonl
from xlpersona.judge import parse_guard
from xlpersona.rubric import judge_prompt, relabel

MODEL = "google/gemma-3-27b-it"


def ask(prompts, workers=96):
    from openai import OpenAI

    client = OpenAI(base_url="http://localhost:8000/v1", api_key="x")

    def one(p):
        out = client.chat.completions.create(model=MODEL, messages=[{"role": "user", "content": p}],
                                             temperature=0.0, max_tokens=120)
        t = out.choices[0].message.content or ""
        m = re.search(r"Reason:\s*(.*)", t)
        return (*parse_guard(t), m.group(1).strip() if m else "")

    with ThreadPoolExecutor(workers) as ex:
        res = list(ex.map(one, prompts))
    log("unparsed", sum(s == "unparsed" or r == "unparsed" for s, r, _ in res), "of", len(res))
    return res


def validate():
    rows = read_jsonl(OUT / "judge150.jsonl")
    res = ask([judge_prompt(r["request"], r["reply"]) for r in rows])
    write_jsonl([{"uid": r["uid"], "safety": s, "refusal": f, "reason": why} for r, (s, f, why) in zip(rows, res)],
                OUT / "judge150_rubric.jsonl")


def judge_all():
    en = {r["id"]: r["text"]["en"] for r in load_requests()}
    files = sorted((OUT / "main").glob("*/*.jsonl"))
    files = [f for f in files if "__" in f.name]
    data = {f: read_jsonl(f) for f in files}
    flat = [(f, i) for f in files for i in range(len(data[f]))]
    log("judging", len(flat), "replies in", len(files), "files")
    res = ask([judge_prompt(en[data[f][i]["id"]], data[f][i]["reply"]) for f, i in flat])
    out = {f: [None] * len(data[f]) for f in files}
    for (f, i), (s, r, why) in zip(flat, res):
        out[f][i] = relabel(data[f][i], s, r, why)
    for f in files:
        write_jsonl(out[f], OUT / "main_rj" / f.parent.name / f.name)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--validate", action="store_true")
    ap.add_argument("--all", action="store_true")
    a = ap.parse_args()
    p = serve(MODEL)
    try:
        validate() if a.validate else judge_all()
    finally:
        p.kill()
