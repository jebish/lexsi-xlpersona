import argparse
import json
import shutil
import subprocess
import time
import urllib.request
from pathlib import Path

NEW = ["hi_rom", "ne_rom", "hi_cm", "ne_cm"]
CANDIDATES = ["Qwen/Qwen3-32B", "google/gemma-3-27b-it"]
API = "http://localhost:8000/v1"


def serve(model):
    p = subprocess.Popen(["vllm", "serve", model, "--port", "8000", "--max-model-len", "4096",
                          "--gpu-memory-utilization", "0.92", "--served-model-name", model])
    for _ in range(240):
        if p.poll() is not None:
            raise RuntimeError(f"vllm exited with {p.returncode} for {model}")
        try:
            urllib.request.urlopen("http://localhost:8000/health", timeout=5)
            return p
        except Exception:
            time.sleep(10)
    p.kill()
    raise RuntimeError(f"vllm did not start for {model}")


def compare(out):
    from openai import OpenAI

    from xlpersona.curate import looks_romanized_indic, transform
    from xlpersona.data import load_requests, select
    from xlpersona.io import write_jsonl

    rows = load_requests()
    sample = select(rows, True, "find")[::10][:5] + select(rows, False, "find")[::10][:5]
    res = []
    for m in CANDIDATES:
        try:
            p = serve(m)
        except Exception as e:
            print("SKIP", m, e)
            continue
        client = OpenAI(base_url=API, api_key="EMPTY")
        for cond in NEW:
            lang, kind = cond.split("_")
            for r, v in zip(sample, transform(client, m, sample, lang, kind)):
                res.append({"model": m, "id": r["id"], "cond": cond, "native": r["text"][lang], "en": r["text"]["en"],
                            "variant": v, "check": looks_romanized_indic(v, lang)})
        p.terminate()
        p.wait()
    write_jsonl(res, out / "variants_compare.jsonl")
    for m in CANDIDATES:
        mine = [x for x in res if x["model"] == m]
        if mine:
            print(f"{m}: check pass {sum(x['check'] for x in mine)}/{len(mine)}")
    for x in res:
        print(f"[{x['model'].split('/')[1]}|{x['cond']}|{x['id']}|{'ok' if x['check'] else 'BAD'}] {x['variant']}")


def full(model, out, smoke):
    from openai import OpenAI

    from xlpersona.curate import length_ok, looks_romanized_indic, run_gate, transform
    from xlpersona.data import load_requests
    from xlpersona.io import log, write_json, write_jsonl

    rows = load_requests()[: 8 if smoke else None]
    p = serve(model)
    client = OpenAI(base_url=API, api_key="EMPTY")
    results, stages = [], {}
    try:
        for cond in NEW:
            lang, kind = cond.split("_")
            texts = dict(zip([r["id"] for r in rows], transform(client, model, rows, lang, kind)))
            attempt = {i: 1 for i in texts}
            gate = None
            for rnd in (1, 2):
                todo = [r for r in rows if gate is None or not gate[r["id"]]["passed"]
                        or not looks_romanized_indic(texts[r["id"]], lang)
                        or not length_ok(texts[r["id"]], r["text"]["en"], r["text"][lang])]
                if rnd == 2:
                    if not todo:
                        break
                    redo = transform(client, model, todo, lang, kind, temperature=0.7)
                    for r, v in zip(todo, redo):
                        texts[r["id"]], attempt[r["id"]] = v, 2
                sub = [{**r, "text": {**r["text"], cond: texts[r["id"]]}} for r in (rows if rnd == 1 else todo)]
                g, counts = run_gate(sub, cond, model, API, out / "curation" / (cond if rnd == 1 else f"{cond}_retry"))
                gate = {**(gate or {}), **g}
                stages[f"{cond}_round{rnd}"] = counts
                log(cond, "round", rnd, "gate passed", sum(v["passed"] for v in g.values()), "/", len(g))
            for r in rows:
                i, g = r["id"], gate[r["id"]]
                ok = looks_romanized_indic(texts[i], lang) and length_ok(texts[i], r["text"]["en"], r["text"][lang])
                results.append({"id": i, "cond": cond, "text": texts[i], "source": "vllm", "model": model,
                                "attempt": attempt[i], "check_ok": ok, "gate_passed": g["passed"],
                                "gate_score": g["score"], "gate_reason": g["reason"],
                                "gate_failed": not (ok and g["passed"])})
    finally:
        p.terminate()
    write_jsonl(results, out / "variants.jsonl")
    summ = {c: {"n": sum(x["cond"] == c for x in results),
                "gate_failed": sum(x["gate_failed"] for x in results if x["cond"] == c),
                "retried": sum(x["attempt"] == 2 for x in results if x["cond"] == c)} for c in NEW}
    write_json({"model": model, "per_cond": summ, "stages": stages}, out / "curation_run.json")
    print(json.dumps(summ, indent=1))


def repair(model, out):
    from openai import OpenAI

    from xlpersona.curate import problems, repair_prompt, run_gate, transform
    from xlpersona.data import load_requests
    from xlpersona.io import log, read_jsonl, write_json, write_jsonl

    rows = {r["id"]: r for r in load_requests()}
    if not (out / "variants_round12.jsonl").exists():
        shutil.copy(out / "variants.jsonl", out / "variants_round12.jsonl")
    res = read_jsonl(out / "variants_round12.jsonl")

    def probs(x, text=None, passed=None):
        r, lang = rows[x["id"]], x["cond"][:2]
        return problems(text or x["text"], r["text"]["en"], r["text"][lang], lang,
                        x["gate_passed"] if passed is None else passed)

    p = serve(model)
    client = OpenAI(base_url=API, api_key="EMPTY")
    stages = {}
    try:
        for cond in NEW:
            lang, kind = cond.split("_")
            for rnd, temp in ((3, 0.3), (4, 0.7)):
                bad = [x for x in res if x["cond"] == cond and probs(x)]
                if not bad:
                    break
                todo = [rows[x["id"]] for x in bad]
                prompts = {x["id"]: repair_prompt(lang, kind, rows[x["id"]]["text"][lang], rows[x["id"]]["text"]["en"],
                                                  x["text"], probs(x)) for x in bad}
                new = transform(client, model, todo, lang, kind, temperature=temp, prompts=prompts)
                sub = [{**r, "text": {**r["text"], cond: v}} for r, v in zip(todo, new)]
                g, counts = run_gate(sub, cond, model, API, out / "curation" / f"{cond}_repair{rnd}")
                stages[f"{cond}_repair{rnd}"] = counts
                fixed = 0
                for x, v in zip(bad, new):
                    gx = g[x["id"]]
                    if not probs(x, v, gx["passed"]):
                        x.update(text=v, attempt=rnd, check_ok=True, gate_passed=True, gate_score=gx["score"],
                                 gate_reason=gx["reason"])
                        fixed += 1
                log(cond, "repair round", rnd, "fixed", fixed, "/", len(bad))
    finally:
        p.terminate()
    for x in res:
        x["problems"] = probs(x)
        x["gate_failed"] = bool(x["problems"])
    write_jsonl(res, out / "variants.jsonl")
    summ = {c: {"n": sum(x["cond"] == c for x in res), "gate_failed": sum(x["gate_failed"] for x in res if x["cond"] == c),
                "repaired": sum(x["attempt"] >= 3 for x in res if x["cond"] == c)} for c in NEW}
    write_json({"model": model, "per_cond": summ, "stages": stages}, out / "curation_repair.json")
    print(json.dumps(summ, indent=1))


def apply(path):
    from xlpersona.data import load_requests, save_requests
    from xlpersona.io import ROOT, read_jsonl

    rows = {r["id"]: r for r in load_requests()}
    for v in read_jsonl(path):
        rows[v["id"]]["text"][v["cond"]] = v["text"]
        rows[v["id"]].setdefault("meta", {})[v["cond"]] = {k: v[k] for k in
                                                            ("source", "model", "attempt", "gate_score", "gate_failed")}
    save_requests(list(rows.values()))
    src = Path(path).parent / "curation"
    if src.exists():
        shutil.copytree(src, ROOT / "data" / "curation", dirs_exist_ok=True)
    print("applied", path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--compare", action="store_true")
    ap.add_argument("--model")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--apply")
    ap.add_argument("--repair", action="store_true")
    a = ap.parse_args()
    from xlpersona.io import OUT

    if a.apply:
        apply(a.apply)
    elif a.repair:
        repair(a.model, OUT)
    elif a.compare:
        compare(OUT)
    else:
        full(a.model, OUT, a.smoke)


if __name__ == "__main__":
    main()
