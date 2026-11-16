---
tags:
- curatorkit
configs:
- config_name: sft_alpaca
  default: true
  description: curatorkit sft_alpaca export, sha256 6fd573d161a459b84072760e783542692827c736f2de7a6a69c78a7dd42619b5
  data_files:
  - split: train
    path: sft_alpaca.jsonl
- config_name: sft_sharegpt
  description: curatorkit sft_sharegpt export, sha256 6330dd22047e302ed2dc464026b568b8acabe0858a366d01a15a5c66a5053d99
  data_files:
  - split: train
    path: sft_sharegpt.jsonl
- config_name: sft_messages
  description: curatorkit sft_messages export, sha256 627d442df6ca781cf6668bd672c95cfc192ef2c73bb3704ff767be5040e74bf0
  data_files:
  - split: train
    path: sft_messages.jsonl
---

# Dataset Card: xlpersona_ne_cm

## Summary

- **Run timestamp**: 2026-11-14T13:09:18.392035Z
- **Wall clock time**: 12.3s
- **Pipeline config hash**: `ebbbd07fd9db364b`

## Source Documents

  - Unknown

## Pipeline Stages

| Step | Input | Passed | Recovered | Rejected | Forward |
|------|-------|--------|-----------|----------|---------|
| JSONLReader | 40 | 40 | — | 0 | 40 |
| SchemaGate | 40 | 40 | 0 | 0 | 40 |
| ExactDeduplicator | 40 | 40 | — | — | 40 |
| TextCleaner | 40 | 40 | — | — | 40 |
| SecretsGate | 40 | 40 | 0 | 0 | 40 |
| RewardGate | 40 | 36 | 0 | 4 | 36 |

## Gate Pass Rates and Rejection Breakdown

- **JSONLReader**: 40/0 passed (N/A), 0 rejected
- **SchemaGate**: 40/40 passed (100.0%), 0 rejected
- **SecretsGate**: 40/40 passed (100.0%), 0 rejected
- **RewardGate**: 36/40 passed (90.0%), 4 rejected


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
| `sft_alpaca` | train (36) | `instruction`: string<br>`input`: string (empty when there is no input)<br>`output`: string |
| `sft_sharegpt` | train (36) | `conversations`: list of {from, value}; from is system, human or gpt |
| `sft_messages` | train (36) | `messages`: list of {role, content}; role is system, user or assistant |
