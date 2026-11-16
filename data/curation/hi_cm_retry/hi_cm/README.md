---
tags:
- curatorkit
configs:
- config_name: sft_alpaca
  default: true
  description: curatorkit sft_alpaca export, sha256 3988abf622a7ae68f55d50cef52aa1d5f16e5248b68f989bbc81638b3d576210
  data_files:
  - split: train
    path: sft_alpaca.jsonl
- config_name: sft_sharegpt
  description: curatorkit sft_sharegpt export, sha256 fb8df9c61482976ec6daf172349859883ded0b9577e90c5d1dc0c1cbf4fef792
  data_files:
  - split: train
    path: sft_sharegpt.jsonl
- config_name: sft_messages
  description: curatorkit sft_messages export, sha256 31c801d111d35c8eca323fc9283a4155f414e8218fc045b010cd2487aa4e7522
  data_files:
  - split: train
    path: sft_messages.jsonl
---

# Dataset Card: xlpersona_hi_cm

## Summary

- **Run timestamp**: 2026-11-14T12:56:52.988348Z
- **Wall clock time**: 1.8s
- **Pipeline config hash**: `c51929553089edf0`

## Source Documents

  - Unknown

## Pipeline Stages

| Step | Input | Passed | Recovered | Rejected | Forward |
|------|-------|--------|-----------|----------|---------|
| JSONLReader | 23 | 23 | — | 0 | 23 |
| SchemaGate | 23 | 23 | 0 | 0 | 23 |
| ExactDeduplicator | 23 | 23 | — | — | 23 |
| TextCleaner | 23 | 23 | — | — | 23 |
| SecretsGate | 23 | 23 | 0 | 0 | 23 |
| RewardGate | 23 | 23 | 0 | 0 | 23 |

## Gate Pass Rates and Rejection Breakdown

- **JSONLReader**: 23/0 passed (N/A), 0 rejected
- **SchemaGate**: 23/23 passed (100.0%), 0 rejected
- **SecretsGate**: 23/23 passed (100.0%), 0 rejected
- **RewardGate**: 23/23 passed (100.0%), 0 rejected


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
| `sft_alpaca` | train (23) | `instruction`: string<br>`input`: string (empty when there is no input)<br>`output`: string |
| `sft_sharegpt` | train (23) | `conversations`: list of {from, value}; from is system, human or gpt |
| `sft_messages` | train (23) | `messages`: list of {role, content}; role is system, user or assistant |
