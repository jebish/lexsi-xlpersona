---
tags:
- curatorkit
configs:
- config_name: sft_alpaca
  default: true
  description: curatorkit sft_alpaca export, sha256 1b44858312c28b58f23c40fc122de97a584d6aa29df8da4f4baf29d31ed87478
  data_files:
  - split: train
    path: sft_alpaca.jsonl
- config_name: sft_sharegpt
  description: curatorkit sft_sharegpt export, sha256 59cf5c4dbb417affe5f9f3faff7e5f3554b075e5ba138c4404605552062c31e0
  data_files:
  - split: train
    path: sft_sharegpt.jsonl
- config_name: sft_messages
  description: curatorkit sft_messages export, sha256 6803fe32dbe9b93be1d8c0de6ac61170b75febea19443287f51d1dcd311f002f
  data_files:
  - split: train
    path: sft_messages.jsonl
---

# Dataset Card: xlpersona_ne_rom

## Summary

- **Run timestamp**: 2026-11-14T12:56:19.880148Z
- **Wall clock time**: 12.3s
- **Pipeline config hash**: `5bff478a0434ba09`

## Source Documents

  - Unknown

## Pipeline Stages

| Step | Input | Passed | Recovered | Rejected | Forward |
|------|-------|--------|-----------|----------|---------|
| JSONLReader | 47 | 47 | — | 0 | 47 |
| SchemaGate | 47 | 47 | 0 | 0 | 47 |
| ExactDeduplicator | 47 | 47 | — | — | 47 |
| TextCleaner | 47 | 47 | — | — | 47 |
| SecretsGate | 47 | 47 | 0 | 0 | 47 |
| RewardGate | 47 | 43 | 0 | 4 | 43 |

## Gate Pass Rates and Rejection Breakdown

- **JSONLReader**: 47/0 passed (N/A), 0 rejected
- **SchemaGate**: 47/47 passed (100.0%), 0 rejected
- **SecretsGate**: 47/47 passed (100.0%), 0 rejected
- **RewardGate**: 43/47 passed (91.5%), 4 rejected


**Rejection reasons:**
  - `judge_error:JudgeParseError`: 4

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
| `sft_alpaca` | train (43) | `instruction`: string<br>`input`: string (empty when there is no input)<br>`output`: string |
| `sft_sharegpt` | train (43) | `conversations`: list of {from, value}; from is system, human or gpt |
| `sft_messages` | train (43) | `messages`: list of {role, content}; role is system, user or assistant |
