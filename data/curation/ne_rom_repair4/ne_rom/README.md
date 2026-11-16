---
tags:
- curatorkit
configs:
- config_name: sft_alpaca
  default: true
  description: curatorkit sft_alpaca export, sha256 f6e9560dbb3037c913933d59aaf6b889b093d4ccb197bf28386d9439617ef90d
  data_files:
  - split: train
    path: sft_alpaca.jsonl
- config_name: sft_sharegpt
  description: curatorkit sft_sharegpt export, sha256 8079d529d6772a35a6e9c255acb6ac46422db92d097ca4c0d309913c2fb77764
  data_files:
  - split: train
    path: sft_sharegpt.jsonl
- config_name: sft_messages
  description: curatorkit sft_messages export, sha256 fe66784fe0522659232f8de4f8a8e0a84c431fb4a314487d6a072023ce29ab9c
  data_files:
  - split: train
    path: sft_messages.jsonl
---

# Dataset Card: xlpersona_ne_rom

## Summary

- **Run timestamp**: 2026-11-14T13:08:30.644213Z
- **Wall clock time**: 9.4s
- **Pipeline config hash**: `873b2e9a53cc38ee`

## Source Documents

  - Unknown

## Pipeline Stages

| Step | Input | Passed | Recovered | Rejected | Forward |
|------|-------|--------|-----------|----------|---------|
| JSONLReader | 9 | 9 | — | 0 | 9 |
| SchemaGate | 9 | 9 | 0 | 0 | 9 |
| ExactDeduplicator | 9 | 9 | — | — | 9 |
| TextCleaner | 9 | 9 | — | — | 9 |
| SecretsGate | 9 | 9 | 0 | 0 | 9 |
| RewardGate | 9 | 7 | 0 | 2 | 7 |

## Gate Pass Rates and Rejection Breakdown

- **JSONLReader**: 9/0 passed (N/A), 0 rejected
- **SchemaGate**: 9/9 passed (100.0%), 0 rejected
- **SecretsGate**: 9/9 passed (100.0%), 0 rejected
- **RewardGate**: 7/9 passed (77.8%), 2 rejected


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
| `sft_alpaca` | train (7) | `instruction`: string<br>`input`: string (empty when there is no input)<br>`output`: string |
| `sft_sharegpt` | train (7) | `conversations`: list of {from, value}; from is system, human or gpt |
| `sft_messages` | train (7) | `messages`: list of {role, content}; role is system, user or assistant |
