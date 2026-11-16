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
