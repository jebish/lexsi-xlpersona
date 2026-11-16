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
