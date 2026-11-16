---
tags:
- curatorkit
configs:
- config_name: sft_alpaca
  default: true
  description: curatorkit sft_alpaca export, sha256 fb4796fddf3e8aeae4772bc1a8e7c167a1a127c11081016782be915bda2e0cd5
  data_files:
  - split: train
    path: sft_alpaca.jsonl
- config_name: sft_sharegpt
  description: curatorkit sft_sharegpt export, sha256 70ba8917a20d8d21ca1cad703417f997888e80cba68fc454403781807169a347
  data_files:
  - split: train
    path: sft_sharegpt.jsonl
- config_name: sft_messages
  description: curatorkit sft_messages export, sha256 33337a7110574a45259b04c6bc9a7c18e3533fc3a88831ddb762aee5bb80fe8b
  data_files:
  - split: train
    path: sft_messages.jsonl
---

# Dataset Card: xlpersona_hi_cm

## Summary

- **Run timestamp**: 2026-11-14T13:08:36.324350Z
- **Wall clock time**: 2.0s
- **Pipeline config hash**: `936fb55ea0234913`

## Source Documents

  - Unknown

## Pipeline Stages

| Step | Input | Passed | Recovered | Rejected | Forward |
|------|-------|--------|-----------|----------|---------|
| JSONLReader | 20 | 20 | — | 0 | 20 |
| SchemaGate | 20 | 20 | 0 | 0 | 20 |
| ExactDeduplicator | 20 | 20 | — | — | 20 |
| TextCleaner | 20 | 20 | — | — | 20 |
| SecretsGate | 20 | 20 | 0 | 0 | 20 |
| RewardGate | 20 | 20 | 0 | 0 | 20 |

## Gate Pass Rates and Rejection Breakdown

- **JSONLReader**: 20/0 passed (N/A), 0 rejected
- **SchemaGate**: 20/20 passed (100.0%), 0 rejected
- **SecretsGate**: 20/20 passed (100.0%), 0 rejected
- **RewardGate**: 20/20 passed (100.0%), 0 rejected


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
| `sft_alpaca` | train (20) | `instruction`: string<br>`input`: string (empty when there is no input)<br>`output`: string |
| `sft_sharegpt` | train (20) | `conversations`: list of {from, value}; from is system, human or gpt |
| `sft_messages` | train (20) | `messages`: list of {role, content}; role is system, user or assistant |
