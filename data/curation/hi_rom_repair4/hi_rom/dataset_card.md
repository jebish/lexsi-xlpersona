# Dataset Card: xlpersona_hi_rom

## Summary

- **Run timestamp**: 2026-11-14T13:08:05.468222Z
- **Wall clock time**: 8.3s
- **Pipeline config hash**: `ec85ca0b2ae35b47`

## Source Documents

  - Unknown

## Pipeline Stages

| Step | Input | Passed | Recovered | Rejected | Forward |
|------|-------|--------|-----------|----------|---------|
| JSONLReader | 3 | 3 | — | 0 | 3 |
| SchemaGate | 3 | 3 | 0 | 0 | 3 |
| ExactDeduplicator | 3 | 3 | — | — | 3 |
| TextCleaner | 3 | 3 | — | — | 3 |
| SecretsGate | 3 | 3 | 0 | 0 | 3 |
| RewardGate | 3 | 2 | 0 | 1 | 2 |

## Gate Pass Rates and Rejection Breakdown

- **JSONLReader**: 3/0 passed (N/A), 0 rejected
- **SchemaGate**: 3/3 passed (100.0%), 0 rejected
- **SecretsGate**: 3/3 passed (100.0%), 0 rejected
- **RewardGate**: 2/3 passed (66.7%), 1 rejected


**Rejection reasons:**
  - `judge_error:JudgeParseError`: 1

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
