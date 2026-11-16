# Dataset Card: xlpersona_ne_rom

## Summary

- **Run timestamp**: 2026-11-14T12:56:19.880148Z
- **Wall clock time**: 12.3s
- **Pipeline config hash**: `5bff478a0434ba09`

## Source Documents

  - Unknown

## Pipeline Stages

| Step | Input | Passed | Recovered | Rejected | Forward |
|------|-------|--------|-----------|----------|---------|
| JSONLReader | 47 | 47 | — | 0 | 47 |
| SchemaGate | 47 | 47 | 0 | 0 | 47 |
| ExactDeduplicator | 47 | 47 | — | — | 47 |
| TextCleaner | 47 | 47 | — | — | 47 |
| SecretsGate | 47 | 47 | 0 | 0 | 47 |
| RewardGate | 47 | 43 | 0 | 4 | 43 |

## Gate Pass Rates and Rejection Breakdown

- **JSONLReader**: 47/0 passed (N/A), 0 rejected
- **SchemaGate**: 47/47 passed (100.0%), 0 rejected
- **SecretsGate**: 47/47 passed (100.0%), 0 rejected
- **RewardGate**: 43/47 passed (91.5%), 4 rejected


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
