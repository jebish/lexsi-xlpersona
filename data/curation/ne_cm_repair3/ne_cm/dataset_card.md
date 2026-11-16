# Dataset Card: xlpersona_ne_cm

## Summary

- **Run timestamp**: 2026-11-14T13:09:01.207113Z
- **Wall clock time**: 13.1s
- **Pipeline config hash**: `a3a1e0c91670957a`

## Source Documents

  - Unknown

## Pipeline Stages

| Step | Input | Passed | Recovered | Rejected | Forward |
|------|-------|--------|-----------|----------|---------|
| JSONLReader | 54 | 54 | — | 0 | 54 |
| SchemaGate | 54 | 54 | 0 | 0 | 54 |
| ExactDeduplicator | 54 | 54 | — | — | 54 |
| TextCleaner | 54 | 54 | — | — | 54 |
| SecretsGate | 54 | 54 | 0 | 0 | 54 |
| RewardGate | 54 | 51 | 0 | 3 | 51 |

## Gate Pass Rates and Rejection Breakdown

- **JSONLReader**: 54/0 passed (N/A), 0 rejected
- **SchemaGate**: 54/54 passed (100.0%), 0 rejected
- **SecretsGate**: 54/54 passed (100.0%), 0 rejected
- **RewardGate**: 51/54 passed (94.4%), 3 rejected


**Rejection reasons:**
  - `judge_error:JudgeParseError`: 3

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
