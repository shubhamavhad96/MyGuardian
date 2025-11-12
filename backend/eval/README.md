# RAG Guardrail Evaluation Benchmark

A reproducible evaluation set of 100 Q/A pairs across health, finance, and general knowledge domains.

## Quick Start

```bash
# Generate benchmark CSV (100 cases)
python eval/generate_benchmark.py

# Run evaluation
python eval/run_eval.py --csv eval/benchmark.csv

# Generate markdown report
python eval/run_eval.py --csv eval/benchmark.csv --report md
```

## Benchmark Format

The benchmark CSV (`benchmark.csv`) contains:

- **domain**: `health`, `finance`, or `general`
- **question**: The user question
- **answer**: The LLM-generated answer to evaluate
- **passages**: JSON array of source passages with `id`, `text`, `source`
- **expect**: Expected decision (`allow`, `repair`, or `block`)

## Metrics Reported

- **Hallucination Rate**: Percentage of answers that need repair or blocking
- **Faithfulness @ threshold**: Percentage meeting faithfulness threshold
- **Coverage @ threshold**: Percentage meeting coverage threshold
- **Repair Rate**: Percentage of answers that were repaired
- **Block Rate**: Percentage of answers that were blocked

## Policy Presets

Compare different policy configurations:

| Preset | Faithfulness Min | Coverage Min | Toxicity Max |
|--------|------------------|--------------|--------------|
| Strict | 0.85 | 0.70 | 0.05 |
| Balanced | 0.15 | 0.60 | 0.04 |
| Lenient | 0.10 | 0.50 | 0.05 |

## Report Output

Running with `--report md` generates a comprehensive Markdown report including:

- Summary statistics
- Metrics breakdown
- Decision distribution
- Performance by domain
- Policy preset comparisons

The report is written to `eval/report.md` and can be pasted into your README.

## Adding Cases

Edit `eval/generate_benchmark.py` to add more cases or domains. The script generates variants to reach 100 total cases.

