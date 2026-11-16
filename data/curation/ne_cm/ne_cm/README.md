---
tags:
- curatorkit
configs:
- config_name: sft_alpaca
  default: true
  description: curatorkit sft_alpaca export, sha256 bb42800d128a01977cb02165a834eeb02c22704364e98fdf5624ee62d882b544
  data_files:
  - split: train
    path: sft_alpaca.jsonl
- config_name: sft_sharegpt
  description: curatorkit sft_sharegpt export, sha256 7982ce0d24d955e5798c6bb5663db927d5a868ac022f2a5052e6f8ec2b278b1e
  data_files:
  - split: train
    path: sft_sharegpt.jsonl
- config_name: sft_messages
  description: curatorkit sft_messages export, sha256 ef9527f38ab20fccc225b058ab83494a5295893e262d3e66d573a2c81edbc2cd
  data_files:
  - split: train
    path: sft_messages.jsonl
---

# Dataset Card: xlpersona_ne_cm

## Summary

- **Run timestamp**: 2026-11-14T12:57:41.632823Z
- **Wall clock time**: 36.4s
- **Pipeline config hash**: `cd471ee31076f471`

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
| RewardGate | 200 | 185 | 0 | 15 | 185 |

## Gate Pass Rates and Rejection Breakdown

- **JSONLReader**: 200/0 passed (N/A), 0 rejected
- **SchemaGate**: 200/200 passed (100.0%), 0 rejected
- **SecretsGate**: 200/200 passed (100.0%), 0 rejected
- **RewardGate**: 185/200 passed (92.5%), 15 rejected


**Rejection reasons:**
  - `judge_error:JudgeParseError`: 15

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
| `sft_alpaca` | train (185) | `instruction`: string<br>`input`: string (empty when there is no input)<br>`output`: string |
| `sft_sharegpt` | train (185) | `conversations`: list of {from, value}; from is system, human or gpt |
| `sft_messages` | train (185) | `messages`: list of {role, content}; role is system, user or assistant |
