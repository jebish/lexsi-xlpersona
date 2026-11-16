---
tags:
- curatorkit
configs:
- config_name: sft_alpaca
  default: true
  description: curatorkit sft_alpaca export, sha256 3fad7cf9a94cfa0b8baccf76d238ec05560f688531b56c1383c4ee1e87d85505
  data_files:
  - split: train
    path: sft_alpaca.jsonl
- config_name: sft_sharegpt
  description: curatorkit sft_sharegpt export, sha256 4500f72a7bfcec4295ca9ad5b15f0f525e0accf1416d02276e0f85a016b67ed6
  data_files:
  - split: train
    path: sft_sharegpt.jsonl
- config_name: sft_messages
  description: curatorkit sft_messages export, sha256 d8d75197e5c940b37c65b490afc0616381673059bfe2956a2b925e1a6a16f7b3
  data_files:
  - split: train
    path: sft_messages.jsonl
---

# Dataset Card: xlpersona_ne_cm

## Summary

- **Run timestamp**: 2026-11-14T13:09:01.207113Z
- **Wall clock time**: 13.1s
- **Pipeline config hash**: `a3a1e0c91670957a`

## Source Documents

  - Unknown

## Pipeline Stages

| Step | Input | Passed | Recovered | Rejected | Forward |
|------|-------|--------|-----------|----------|---------|
| JSONLReader | 54 | 54 | — | 0 | 54 |
| SchemaGate | 54 | 54 | 0 | 0 | 54 |
| ExactDeduplicator | 54 | 54 | — | — | 54 |
| TextCleaner | 54 | 54 | — | — | 54 |
| SecretsGate | 54 | 54 | 0 | 0 | 54 |
| RewardGate | 54 | 51 | 0 | 3 | 51 |

## Gate Pass Rates and Rejection Breakdown

- **JSONLReader**: 54/0 passed (N/A), 0 rejected
- **SchemaGate**: 54/54 passed (100.0%), 0 rejected
- **SecretsGate**: 54/54 passed (100.0%), 0 rejected
- **RewardGate**: 51/54 passed (94.4%), 3 rejected


**Rejection reasons:**
  - `judge_error:JudgeParseError`: 3

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
| `sft_alpaca` | train (51) | `instruction`: string<br>`input`: string (empty when there is no input)<br>`output`: string |
| `sft_sharegpt` | train (51) | `conversations`: list of {from, value}; from is system, human or gpt |
| `sft_messages` | train (51) | `messages`: list of {role, content}; role is system, user or assistant |
