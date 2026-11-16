---
tags:
- curatorkit
configs:
- config_name: sft_alpaca
  default: true
  description: curatorkit sft_alpaca export, sha256 8230c436a19dada540b8812ffd1783baabb4202f6fc93bf7d37a875cf56ca3dd
  data_files:
  - split: train
    path: sft_alpaca.jsonl
- config_name: sft_sharegpt
  description: curatorkit sft_sharegpt export, sha256 9d9e286c1220fc42fae5b771722a8fb74e037940143187094367980cee4f8367
  data_files:
  - split: train
    path: sft_sharegpt.jsonl
- config_name: sft_messages
  description: curatorkit sft_messages export, sha256 e306b9384a00b811e797ffce7ed028e6b127888f9927eb2c44a98566a5467934
  data_files:
  - split: train
    path: sft_messages.jsonl
---

# Dataset Card: xlpersona_hi_rom

## Summary

- **Run timestamp**: 2026-11-14T13:07:56.005010Z
- **Wall clock time**: 1.4s
- **Pipeline config hash**: `022ebac84d98b05c`

## Source Documents

  - Unknown

## Pipeline Stages

| Step | Input | Passed | Recovered | Rejected | Forward |
|------|-------|--------|-----------|----------|---------|
| JSONLReader | 6 | 6 | — | 0 | 6 |
| SchemaGate | 6 | 6 | 0 | 0 | 6 |
| ExactDeduplicator | 6 | 6 | — | — | 6 |
| TextCleaner | 6 | 6 | — | — | 6 |
| SecretsGate | 6 | 6 | 0 | 0 | 6 |
| RewardGate | 6 | 6 | 0 | 0 | 6 |

## Gate Pass Rates and Rejection Breakdown

- **JSONLReader**: 6/0 passed (N/A), 0 rejected
- **SchemaGate**: 6/6 passed (100.0%), 0 rejected
- **SecretsGate**: 6/6 passed (100.0%), 0 rejected
- **RewardGate**: 6/6 passed (100.0%), 0 rejected


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
| `sft_alpaca` | train (6) | `instruction`: string<br>`input`: string (empty when there is no input)<br>`output`: string |
| `sft_sharegpt` | train (6) | `conversations`: list of {from, value}; from is system, human or gpt |
| `sft_messages` | train (6) | `messages`: list of {role, content}; role is system, user or assistant |
