---
tags:
- curatorkit
configs:
- config_name: sft_alpaca
  default: true
  description: curatorkit sft_alpaca export, sha256 2bcbf33d2eb84507efefb43b070488402ef641099e83fc914920e78ea80c6a99
  data_files:
  - split: train
    path: sft_alpaca.jsonl
- config_name: sft_sharegpt
  description: curatorkit sft_sharegpt export, sha256 4580c75a8a639e39ba21bd09762195c293e797e551a3dfa53546c634a4859890
  data_files:
  - split: train
    path: sft_sharegpt.jsonl
- config_name: sft_messages
  description: curatorkit sft_messages export, sha256 06a2b382ca18f66575e018238d002e57dac94181fff561e541b289569c31f933
  data_files:
  - split: train
    path: sft_messages.jsonl
---

# Dataset Card: xlpersona_ne_cm

## Summary

- **Run timestamp**: 2026-11-14T12:58:04.511442Z
- **Wall clock time**: 15.7s
- **Pipeline config hash**: `cbe9a7720647348d`

## Source Documents

  - Unknown

## Pipeline Stages

| Step | Input | Passed | Recovered | Rejected | Forward |
|------|-------|--------|-----------|----------|---------|
| JSONLReader | 83 | 83 | — | 0 | 83 |
| SchemaGate | 83 | 83 | 0 | 0 | 83 |
| ExactDeduplicator | 83 | 83 | — | — | 83 |
| TextCleaner | 83 | 83 | — | — | 83 |
| SecretsGate | 83 | 83 | 0 | 0 | 83 |
| RewardGate | 83 | 76 | 0 | 7 | 76 |

## Gate Pass Rates and Rejection Breakdown

- **JSONLReader**: 83/0 passed (N/A), 0 rejected
- **SchemaGate**: 83/83 passed (100.0%), 0 rejected
- **SecretsGate**: 83/83 passed (100.0%), 0 rejected
- **RewardGate**: 76/83 passed (91.6%), 7 rejected


**Rejection reasons:**
  - `judge_error:JudgeParseError`: 7

## Deduplication

  - exact_duplicates_removed: 0

## Known Limitations

- No MinHash deduplication applied.
- Table extraction requires `extract_tables: true` on the PDF reader and MinerU with GPU support. Disabled by default.
- Token counting uses a whitespace tokenizer by default. For exact LLM context window
  enforcement, enable `use_tiktoken: true` in the SchemaGate config.
- Both within-run (MinHash/Diversity) and cross-run (EmbeddingDeduplicator) deduplication
  are available. Cross-run dedup persists an embedding index across runs; use
  `embedding_reset_index: true` to start fresh.

## Reproduction

```bash
pip install curatorkit
curatorkit run pipeline.yaml --output-dir ./out/
```

## Tool Versions

- **curatorkit**: 0.1.27
- **python**: 3.12.10

## Configs

Load one with `datasets.load_dataset("<this folder or Hub repo>", "<config>")`.

| Config | Splits (rows) | Columns |
|--------|---------------|---------|
| `sft_alpaca` | train (76) | `instruction`: string<br>`input`: string (empty when there is no input)<br>`output`: string |
| `sft_sharegpt` | train (76) | `conversations`: list of {from, value}; from is system, human or gpt |
| `sft_messages` | train (76) | `messages`: list of {role, content}; role is system, user or assistant |
