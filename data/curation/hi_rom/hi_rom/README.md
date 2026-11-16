---
tags:
- curatorkit
configs:
- config_name: sft_alpaca
  default: true
  description: curatorkit sft_alpaca export, sha256 f4f09b8021fd5dd113540104eadb3bea7c6928ae420df19df9fa55b035552435
  data_files:
  - split: train
    path: sft_alpaca.jsonl
- config_name: sft_sharegpt
  description: curatorkit sft_sharegpt export, sha256 90035dc481670cb712e3e5128c8762695fec90dc94d11df1aad98de401cea95a
  data_files:
  - split: train
    path: sft_sharegpt.jsonl
- config_name: sft_messages
  description: curatorkit sft_messages export, sha256 cb20ca709efd57300c20003d034b755820ffee388dffc1f535870f34d4ca8329
  data_files:
  - split: train
    path: sft_messages.jsonl
---

# Dataset Card: xlpersona_hi_rom

## Summary

- **Run timestamp**: 2026-11-14T12:55:25.651367Z
- **Wall clock time**: 24.0s
- **Pipeline config hash**: `03e6abfc1a8c5e5d`

## Source Documents

  - Unknown

## Pipeline Stages

| Step | Input | Passed | Recovered | Rejected | Forward |
|------|-------|--------|-----------|----------|---------|
| JSONLReader | 200 | 200 | — | 0 | 200 |
| SchemaGate | 200 | 200 | 0 | 0 | 200 |
| ExactDeduplicator | 200 | 200 | — | — | 200 |
| TextCleaner | 200 | 200 | — | — | 200 |
| SecretsGate | 200 | 200 | 0 | 0 | 200 |
| RewardGate | 200 | 199 | 0 | 1 | 199 |

## Gate Pass Rates and Rejection Breakdown

- **JSONLReader**: 200/0 passed (N/A), 0 rejected
- **SchemaGate**: 200/200 passed (100.0%), 0 rejected
- **SecretsGate**: 200/200 passed (100.0%), 0 rejected
- **RewardGate**: 199/200 passed (99.5%), 1 rejected


**Rejection reasons:**
  - `judge_error:JudgeParseError`: 1

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
| `sft_alpaca` | train (199) | `instruction`: string<br>`input`: string (empty when there is no input)<br>`output`: string |
| `sft_sharegpt` | train (199) | `conversations`: list of {from, value}; from is system, human or gpt |
| `sft_messages` | train (199) | `messages`: list of {role, content}; role is system, user or assistant |
