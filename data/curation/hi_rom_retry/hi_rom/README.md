---
tags:
- curatorkit
configs:
- config_name: sft_alpaca
  default: true
  description: curatorkit sft_alpaca export, sha256 4e8bca0f91875701d1e00503a16e26368a3fb1a35e9e71b3cf1e9afd110ad21c
  data_files:
  - split: train
    path: sft_alpaca.jsonl
- config_name: sft_sharegpt
  description: curatorkit sft_sharegpt export, sha256 17d19b36d2daf9c554beba3530bf010fa991823897aa02a67431c70c8e69484b
  data_files:
  - split: train
    path: sft_sharegpt.jsonl
- config_name: sft_messages
  description: curatorkit sft_messages export, sha256 1b2a8bca64839e54d756f01c25ea379cfb3e4f5aaa146e2ab04202f44ff7944e
  data_files:
  - split: train
    path: sft_messages.jsonl
---

# Dataset Card: xlpersona_hi_rom

## Summary

- **Run timestamp**: 2026-11-14T12:55:28.047494Z
- **Wall clock time**: 1.0s
- **Pipeline config hash**: `63c5f2752ce6506b`

## Source Documents

  - Unknown

## Pipeline Stages

| Step | Input | Passed | Recovered | Rejected | Forward |
|------|-------|--------|-----------|----------|---------|
| JSONLReader | 8 | 8 | — | 0 | 8 |
| SchemaGate | 8 | 8 | 0 | 0 | 8 |
| ExactDeduplicator | 8 | 8 | — | — | 8 |
| TextCleaner | 8 | 8 | — | — | 8 |
| SecretsGate | 8 | 8 | 0 | 0 | 8 |
| RewardGate | 8 | 8 | 0 | 0 | 8 |

## Gate Pass Rates and Rejection Breakdown

- **JSONLReader**: 8/0 passed (N/A), 0 rejected
- **SchemaGate**: 8/8 passed (100.0%), 0 rejected
- **SecretsGate**: 8/8 passed (100.0%), 0 rejected
- **RewardGate**: 8/8 passed (100.0%), 0 rejected


**Rejection reasons:**
  - None

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
| `sft_alpaca` | train (8) | `instruction`: string<br>`input`: string (empty when there is no input)<br>`output`: string |
| `sft_sharegpt` | train (8) | `conversations`: list of {from, value}; from is system, human or gpt |
| `sft_messages` | train (8) | `messages`: list of {role, content}; role is system, user or assistant |
