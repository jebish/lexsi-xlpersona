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
