---
tags:
- curatorkit
configs:
- config_name: sft_alpaca
  default: true
  description: curatorkit sft_alpaca export, sha256 360c306acf49e8d502edec05654dcc1b0a015e15b6b1867701dee6e8261341a0
  data_files:
  - split: train
    path: sft_alpaca.jsonl
- config_name: sft_sharegpt
  description: curatorkit sft_sharegpt export, sha256 8262415a2b4df1138265de056f2a504239a9d89e869c166c7508fdef2547284c
  data_files:
  - split: train
    path: sft_sharegpt.jsonl
- config_name: sft_messages
  description: curatorkit sft_messages export, sha256 c3fc3eadcdef84aa8d8bc5e4eedbdf1e2087ccc5493c1126b9cc626323c600be
  data_files:
  - split: train
    path: sft_messages.jsonl
---

# Dataset Card: xlpersona_ne_rom

## Summary

- **Run timestamp**: 2026-11-14T12:56:04.212556Z
- **Wall clock time**: 24.9s
- **Pipeline config hash**: `ddb8a9a3518034c9`

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
| RewardGate | 200 | 196 | 0 | 4 | 196 |

## Gate Pass Rates and Rejection Breakdown

- **JSONLReader**: 200/0 passed (N/A), 0 rejected
- **SchemaGate**: 200/200 passed (100.0%), 0 rejected
- **SecretsGate**: 200/200 passed (100.0%), 0 rejected
- **RewardGate**: 196/200 passed (98.0%), 4 rejected


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
| `sft_alpaca` | train (196) | `instruction`: string<br>`input`: string (empty when there is no input)<br>`output`: string |
| `sft_sharegpt` | train (196) | `conversations`: list of {from, value}; from is system, human or gpt |
| `sft_messages` | train (196) | `messages`: list of {role, content}; role is system, user or assistant |
