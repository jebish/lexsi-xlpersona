# Dataset Card: xlpersona_hi_cm

## Summary

- **Run timestamp**: 2026-11-14T12:56:52.988348Z
- **Wall clock time**: 1.8s
- **Pipeline config hash**: `c51929553089edf0`

## Source Documents

  - Unknown

## Pipeline Stages

| Step | Input | Passed | Recovered | Rejected | Forward |
|------|-------|--------|-----------|----------|---------|
| JSONLReader | 23 | 23 | — | 0 | 23 |
| SchemaGate | 23 | 23 | 0 | 0 | 23 |
| ExactDeduplicator | 23 | 23 | — | — | 23 |
| TextCleaner | 23 | 23 | — | — | 23 |
| SecretsGate | 23 | 23 | 0 | 0 | 23 |
| RewardGate | 23 | 23 | 0 | 0 | 23 |

## Gate Pass Rates and Rejection Breakdown

- **JSONLReader**: 23/0 passed (N/A), 0 rejected
- **SchemaGate**: 23/23 passed (100.0%), 0 rejected
- **SecretsGate**: 23/23 passed (100.0%), 0 rejected
- **RewardGate**: 23/23 passed (100.0%), 0 rejected


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
