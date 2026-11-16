import argparse
import json
from pathlib import Path

BANNED = {"reply", "raw"}
LABEL_KEYS = ("id", "cond", "guardrail", "set", "template", "safety", "refusal", "unsafe_coherent", "refused",
              "degenerate", "plausible")


def build_release_tables(rows, templates, out_dir, summary):
    from xlpersona.conditions import CONDITIONS
    from xlpersona.prompts import stage1_prompt_sets, stage2_prompt_sets

    cat = {r["id"]: r.get("category") for r in rows}
    seen, prompts = set(), []

    def add(p):
        if (p.id, p.cond, p.template) not in seen:
            seen.add((p.id, p.cond, p.template))
            prompts.append({"id": p.id, "cond": p.cond, "template": p.template, "split": p.split,
                            "harmful": p.harmful, "category": cat.get(p.id), "prompt": p.text})

    for p in stage1_prompt_sets(rows, templates):
        add(p)
    for c in CONDITIONS:
        for ps in stage2_prompt_sets(rows, templates, c).values():
            for p in ps:
                add(p)
    labels = []
    for path in sorted(Path(out_dir).glob("*/*.jsonl")):
        cell = path.stem.split("__")[0]
        for line in path.read_text(encoding="utf-8").splitlines():
            r = json.loads(line)
            labels.append({k: (cell if k == "set" else r.get(k)) for k in LABEL_KEYS})
    for table in (prompts, labels):
        for row in table:
            if BANNED & set(row):
                raise ValueError(f"refusing to release a {BANNED & set(row)} column")
    return {"prompts": prompts, "labels": labels, "results": summary}


def dataset_card(tables):
    n_p, n_l = len(tables["prompts"]), len(tables["labels"])
    return f"""---
license: cc-by-nc-4.0
language: [en, hi, ne]
tags: [jailbreak, persona, multilingual, romanization, code-mixing, safety]
configs:
- config_name: prompts
  data_files: prompts/train-*
- config_name: labels
  data_files: labels/train-*
---
# persona-jailbreak-7c

> **Content warning.** The prompts request harmful content, including self-harm, wrapped in persona jailbreaks.
> Use them only to test and improve safety guardrails.

Persona-jailbreak prompts in seven conditions (English; Hindi and Nepali in Devanagari, romanized and code-mixed)
and Qwen3Guard labels for Tiny Aya Global under 14 guardrails.

* `prompts`: {n_p} prompts.
* `labels`: {n_l} labels, one per prompt and guardrail.

Requests from [JailbreakBench](https://huggingface.co/datasets/JailbreakBench/JBB-Behaviors).
Code: [jebish/lexsi-xlpersona](https://github.com/jebish/lexsi-xlpersona).
"""


def push(tables, repo, card):
    from datasets import Dataset
    from huggingface_hub import HfApi

    for name in ("prompts", "labels"):
        Dataset.from_list(tables[name]).push_to_hub(repo, config_name=name, split="train", private=False)
    api = HfApi()
    api.upload_file(path_or_fileobj=json.dumps(tables["results"], indent=1).encode(), path_in_repo="results/summary.json",
                    repo_id=repo, repo_type="dataset")
    api.upload_file(path_or_fileobj=card.encode(), path_in_repo="README.md", repo_id=repo, repo_type="dataset")


if __name__ == "__main__":
    from xlpersona.data import load_requests
    from xlpersona.templates import load_templates

    ap = argparse.ArgumentParser()
    ap.add_argument("out_dir")
    ap.add_argument("--push")
    a = ap.parse_args()
    summary = json.loads(Path("results/summary.json").read_text(encoding="utf-8"))
    t = build_release_tables(load_requests(), load_templates(), a.out_dir, summary)
    card = dataset_card(t)
    print(len(t["prompts"]), "prompts,", len(t["labels"]), "labels")
    if a.push:
        push(t, a.push, card)
        print("pushed", a.push)
    else:
        Path("out/dataset_card.md").write_text(card, encoding="utf-8")
        print("dry run; card at out/dataset_card.md")
