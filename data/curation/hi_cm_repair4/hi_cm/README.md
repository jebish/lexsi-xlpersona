---
tags:
- curatorkit
configs:
- config_name: sft_alpaca
  default: true
  description: curatorkit sft_alpaca export, sha256 384565e57692322c70ca59d8e6cb8861c6deec2f47a190b997d55c15be1bdc93
  data_files:
  - split: train
    path: sft_alpaca.jsonl
- config_name: sft_sharegpt
  description: curatorkit sft_sharegpt export, sha256 8f2289936c98c5e3e741ea96c3ec62fd04b034ffbacd734972ae167dc421338e
  data_files:
  - split: train
    path: sft_sharegpt.jsonl
- config_name: sft_messages
  description: curatorkit sft_messages export, sha256 3cc01a422b58d163d66ee84ca84caaa7b689c2452ad884f3b240f7a804e6ff19
  data_files:
  - split: train
    path: sft_messages.jsonl
---

# Dataset Card: xlpersona_hi_cm

## Summary

- **Run timestamp**: 2026-11-14T13:08:41.201894Z
- **Wall clock time**: 1.3s
- **Pipeline config hash**: `e891ee5dbde635b2`

## Source Documents

  - Unknown

## Pipeline Stages

| Step | Input | Passed | Recovered | Rejected | Forward |
|------|-------|--------|-----------|----------|---------|
| JSONLReader | 15 | 15 | — | 0 | 15 |
| SchemaGate | 15 | 15 | 0 | 0 | 15 |
| ExactDeduplicator | 15 | 15 | — | — | 15 |
| TextCleaner | 15 | 15 | — | — | 15 |
| SecretsGate | 15 | 15 | 0 | 0 | 15 |
| RewardGate | 15 | 15 | 0 | 0 | 15 |

## Gate Pass Rates and Rejection Breakdown

- **JSONLReader**: 15/0 passed (N/A), 0 rejected
- **SchemaGate**: 15/15 passed (100.0%), 0 rejected
- **SecretsGate**: 15/15 passed (100.0%), 0 rejected
- **RewardGate**: 15/15 passed (100.0%), 0 rejected


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
| `sft_alpaca` | train (15) | `instruction`: string<br>`input`: string (empty when there is no input)<br>`output`: string |
| `sft_sharegpt` | train (15) | `conversations`: list of {from, value}; from is system, human or gpt |
| `sft_messages` | train (15) | `messages`: list of {role, content}; role is system, user or assistant |
