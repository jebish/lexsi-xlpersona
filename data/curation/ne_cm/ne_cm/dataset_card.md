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
