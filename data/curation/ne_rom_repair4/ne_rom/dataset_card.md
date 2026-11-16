# Dataset Card: xlpersona_ne_rom

## Summary

- **Run timestamp**: 2026-11-14T13:08:30.644213Z
- **Wall clock time**: 9.4s
- **Pipeline config hash**: `873b2e9a53cc38ee`

## Source Documents

  - Unknown

## Pipeline Stages

| Step | Input | Passed | Recovered | Rejected | Forward |
|------|-------|--------|-----------|----------|---------|
| JSONLReader | 9 | 9 | — | 0 | 9 |
| SchemaGate | 9 | 9 | 0 | 0 | 9 |
| ExactDeduplicator | 9 | 9 | — | — | 9 |
| TextCleaner | 9 | 9 | — | — | 9 |
| SecretsGate | 9 | 9 | 0 | 0 | 9 |
| RewardGate | 9 | 7 | 0 | 2 | 7 |

## Gate Pass Rates and Rejection Breakdown

- **JSONLReader**: 9/0 passed (N/A), 0 rejected
- **SchemaGate**: 9/9 passed (100.0%), 0 rejected
- **SecretsGate**: 9/9 passed (100.0%), 0 rejected
- **RewardGate**: 7/9 passed (77.8%), 2 rejected


**Rejection reasons:**
  - `judge_error:JudgeParseError`: 2

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
