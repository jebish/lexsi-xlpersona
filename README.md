# Script, not language? Persona-jailbreak guardrails for Hindi and Nepali

Do activation-level guardrails built from English persona jailbreaks protect a multilingual model when the same
attack arrives in Hindi or Nepali, in Devanagari, romanized, or code-mixed with English?

Model: [Tiny Aya Global](https://huggingface.co/CohereLabs/tiny-aya-global).
Kits: CuratorKIT, SafeTune, AuditKIT.

Write-up: [`docs/article.md`](docs/article.md). Tables: [`results/summary.md`](results/summary.md).

## Contents

* `xlpersona/`: residual hooks (ablate, cap, add), directions, judge, prompts, guardrails, kit wrappers.
* `scripts/`: one script per stage. `modal_app.py` runs them on Modal.
* `data/`: requests in seven conditions, persona templates, CuratorKIT outputs.
* `results/`: tables, figure, judge validation, model card.

## Setup

```bash
pip install torch transformers==5.20.2 safetune==0.1.19 auditkit==1.1.11 curatorkit==0.1.27 modal datasets numpy scikit-learn pytest
python -m pytest -q
```

GPU stages run on Modal and need a `huggingface-secret` with access to the models.

## Reproduce

```bash
python -m modal run modal_app.py --script select_heldout.py --gpu a100
python -m modal run modal_app.py --script gen_variants.py --args "--model google/gemma-3-27b-it" --gpu vllm
python -m modal run modal_app.py --script gen_variants.py --args "--model google/gemma-3-27b-it --repair" --gpu vllm
python -m modal volume get xlpersona xl/variants.jsonl out/variants.jsonl
python scripts/gen_variants.py --apply out/variants.jsonl
python -m modal run --detach modal_app.py --script overnight
python -m modal volume get xlpersona xl/main out/
python -m modal volume get xlpersona xl/mmlu.json out/mmlu.json
python scripts/analyze.py out/main results --mmlu out/mmlu.json
python scripts/pooled_transfer.py out/main results/pooled_transfer.json
python scripts/robustness.py out/main results
python -m modal run modal_app.py --script geometry.py --gpu l4
python -m modal volume get --force xlpersona xl/main/acts_lstar.pt out/acts_lstar.pt
python scripts/geometry.py --acts out/acts_lstar.pt --directions out/main/directions.pt --out results/geometry.json
python -m modal run modal_app.py --script comprehension.py --gpu l4
python scripts/export_labels.py out/main
python scripts/score_labels.py labels/judge_sample_final.csv --out results/judge_validation_final_qwen.json
python scripts/release.py out/main --push <hf-dataset-repo>
python -m modal run modal_app.py --script push_ablated.py --args "--repo <hf-model-repo>" --gpu cpu
```

Run local scripts with the repo root and `scripts/` on `PYTHONPATH`.

Model replies are not included in this repository or the released dataset.

## Licence

Code: MIT. Data and model derivatives: CC-BY-NC-4.0 (Tiny Aya). JailbreakBench requests: MIT.
