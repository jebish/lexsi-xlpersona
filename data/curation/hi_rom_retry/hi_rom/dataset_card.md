# Dataset Card: xlpersona_hi_rom

## Summary

- **Run timestamp**: 2026-11-14T12:55:28.047494Z
- **Wall clock time**: 1.0s
- **Pipeline config hash**: `63c5f2752ce6506b`

## Source Documents

  - Unknown

## Pipeline Stages

| Step | Input | Passed | Recovered | Rejected | Forward |
|------|-------|--------|-----------|----------|---------|
| JSONLReader | 8 | 8 | — | 0 | 8 |
| SchemaGate | 8 | 8 | 0 | 0 | 8 |
| ExactDeduplicator | 8 | 8 | — | — | 8 |
| TextCleaner | 8 | 8 | — | — | 8 |
| SecretsGate | 8 | 8 | 0 | 0 | 8 |
| RewardGate | 8 | 8 | 0 | 0 | 8 |

## Gate Pass Rates and Rejection Breakdown

- **JSONLReader**: 8/0 passed (N/A), 0 rejected
- **SchemaGate**: 8/8 passed (100.0%), 0 rejected
- **SecretsGate**: 8/8 passed (100.0%), 0 rejected
- **RewardGate**: 8/8 passed (100.0%), 0 rejected


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
