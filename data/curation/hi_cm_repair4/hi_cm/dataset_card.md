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
