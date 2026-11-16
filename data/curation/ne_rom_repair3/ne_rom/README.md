---
tags:
- curatorkit
configs:
- config_name: sft_alpaca
  default: true
  description: curatorkit sft_alpaca export, sha256 246827238f27a1011fb48a32def4f2fe89e8c55a16f91f2f7eedb056f19f3aff
  data_files:
  - split: train
    path: sft_alpaca.jsonl
- config_name: sft_sharegpt
  description: curatorkit sft_sharegpt export, sha256 627eef60928b79b1e00e3c7a0a9267b95708cdf542807d82091566c437ca779e
  data_files:
  - split: train
    path: sft_sharegpt.jsonl
- config_name: sft_messages
  description: curatorkit sft_messages export, sha256 bd8b44afb159d89c9723c4299ed9bc1d84d0a2774a15445652ca56c483b46779
  data_files:
  - split: train
    path: sft_messages.jsonl
---

# Dataset Card: xlpersona_ne_rom

## Summary

- **Run timestamp**: 2026-11-14T13:08:19.421930Z
- **Wall clock time**: 11.5s
- **Pipeline config hash**: `e69b03ba83d279f6`

## Source Documents

  - Unknown

## Pipeline Stages

| Step | Input | Passed | Recovered | Rejected | Forward |
|------|-------|--------|-----------|----------|---------|
| JSONLReader | 21 | 21 | — | 0 | 21 |
| SchemaGate | 21 | 21 | 0 | 0 | 21 |
| ExactDeduplicator | 21 | 21 | — | — | 21 |
| TextCleaner | 21 | 21 | — | — | 21 |
| SecretsGate | 21 | 21 | 0 | 0 | 21 |
| RewardGate | 21 | 19 | 0 | 2 | 19 |

## Gate Pass Rates and Rejection Breakdown

- **JSONLReader**: 21/0 passed (N/A), 0 rejected
- **SchemaGate**: 21/21 passed (100.0%), 0 rejected
- **SecretsGate**: 21/21 passed (100.0%), 0 rejected
- **RewardGate**: 19/21 passed (90.5%), 2 rejected


**Rejection reasons:**
  - `judge_error:JudgeParseError`: 2

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
| `sft_alpaca` | train (19) | `instruction`: string<br>`input`: string (empty when there is no input)<br>`output`: string |
| `sft_sharegpt` | train (19) | `conversations`: list of {from, value}; from is system, human or gpt |
| `sft_messages` | train (19) | `messages`: list of {role, content}; role is system, user or assistant |
