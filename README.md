# Elections go bananas: A First Large-scale Multilingual Study of Pluralia Tantum using LLMs

This repository includes the evaluation scripts used in the paper.

## `llm_classifier` — LLM Annotation & Evaluation Toolkit

A modular Python package for annotating linguistic data with LLMs and evaluating the results.

### Installation

```bash
pip install openai pandas scikit-learn numpy matplotlib seaborn
```

### Features

- **Multi-model support**: Runs the same prompt across multiple OpenAI and DeepSeek models in a single command.
- **Resume-safe**: If a run is interrupted, re-running the same command will pick up where it left off.
- **Flexible prompts**: Reference any CSV column in your prompt template via `{column_name}` placeholders.
- **Robust parsing**: Extracts JSON from messy LLM outputs using regex + `ast.literal_eval` fallback.
- **Multi-label evaluation**: Computes Exact Match Accuracy, Jaccard Similarity, and Micro-F1 scores.
- **Publication-quality plots**: Generates bar charts comparing model performance across annotation categories.

### Supported Models

| Provider | Models |
|----------|--------|
| OpenAI | `gpt-4o`, `gpt-4o-mini`, `chatgpt-4o-latest`, `o1`, `o3-mini`, `o3`, `gpt-4.1-*` |
| DeepSeek | `deepseek-chat`, `deepseek-reasoner` |

---

## Full Pipeline

### Step 1 — Annotate

```bash
# Zero-shot
python -m llm_classifier.cli annotate \
    -i data/your_data.csv \
    -o results/ \
    -m gpt-4o-mini deepseek-chat \
    --openai-key $OPENAI_API_KEY \
    --deepseek-key $DEEPSEEK_API_KEY \
    --system-message config/system_message.txt \
    --prompt-template config/prompt_zeroshot.txt \
    --prompt-columns text_clean

# Few-shot (same command, different prompt template)
python -m llm_classifier.cli annotate \
    -i data/your_data.csv \
    -o results/ \
    -m gpt-4o gpt-4o-mini \
    --openai-key $OPENAI_API_KEY \
    --system-message config/system_message.txt \
    --prompt-template config/prompt_fewshot.txt \
    --prompt-columns text_clean \
    --temperature 0.7
```

### Step 2 — Parse outputs

Extract structured JSON from raw LLM responses:

```bash
python parse_outputs.py --output-dir results/
```

This scans all model subdirectories in `results/`, extracts JSON from output columns, and writes parsed fields back into the CSVs. A `parsing_report.csv` is generated listing any rows that failed to parse.

### Step 3 — Evaluate

Compare predictions against ground truth:

```bash
python evaluate.py \
    --data data/ \
    --predictions results/ \
    --output evaluations/
```

**Outputs:**
- `evaluations/<dataset>_evaluated.csv` — per-dataset metrics
- `evaluations/all_datasets_evaluated.csv` — combined results
- `evaluations/summary_by_model_label.csv` — averaged by model & label

### Step 4 — Plot results

Generate publication-quality bar charts:

```bash
# Overall plot (all languages averaged)
python plot_results.py \
    --input evaluations/summary_by_model_label.csv \
    --metric jaccard_score

# Per-language plots
python plot_results.py \
    --input evaluations/all_datasets_evaluated.csv \
    --by-language \
    --lang-map lang_map.json

# Other metrics: exact_match_accuracy, f1_micro, precision_micro, recall_micro
python plot_results.py \
    --input evaluations/summary_by_model_label.csv \
    --metric exact_match_accuracy
```

Figures are saved to `figs/` as both PDF and PNG.

For `--by-language`, provide a JSON file mapping dataset names to languages:
```json
{
    "peregovor": "Russian",
    "koska": "Russian",
    "condoglianza": "Italian",
    "urna": "Italian",
    "banana": "English",
    "hostility": "English"
}
```

---

## Python API

```python
from llm_classifier import Annotator, Parser, Evaluator

# Annotate
annotator = Annotator(
    openai_api_key="sk-...",
    models=["gpt-4o-mini"],
    system_message_path="config/system_message.txt",
    prompt_template_path="config/prompt_zeroshot.txt",
)
annotator.run("data/input.csv", output_dir="results/")

# Parse
parser = Parser(verbose=True)
df_parsed = parser.parse_csv("results/output_gpt-4o-mini.csv")

# Evaluate
evaluator = Evaluator()
metrics = evaluator.evaluate(df_parsed, "data/gold_standard.csv")
print(metrics)
```

## Citation

```bibtex
@inproceedings{spaziani-etal-2026-elections,
    title = "Elections go bananas: A First Large-scale Multilingual Study of Pluralia Tantum using {LLM}s",
    author = "Spaziani, Elena  and
      Zeinalipour, Kamyar  and
      Cassotti, Pierluigi  and
      Tahmasebi, Nina",
    editor = "Demberg, Vera  and
      Inui, Kentaro  and
      Marquez, Llu{\'i}s",
    booktitle = "Proceedings of the 19th Conference of the {E}uropean Chapter of the {A}ssociation for {C}omputational {L}inguistics (Volume 1: Long Papers)",
    month = mar,
    year = "2026",
    address = "Rabat, Morocco",
    publisher = "Association for Computational Linguistics",
    url = "https://aclanthology.org/2026.eacl-long.308/",
    doi = "10.18653/v1/2026.eacl-long.308",
    pages = "6547--6570",
    ISBN = "979-8-89176-380-7",
    abstract = "In this paper, we study the expansion of pluralia tantum, i.e., defective nouns which lack a singular form, like scissors. We base our work on an annotation framework specifically developed for the study of lexicalization of pluralia tantum, namely Lexicalization profiles. On a corresponding hand-annotated testset, we show that the OpenAI and DeepSeek models provide useful annotators for semantic, syntactic and sense categories, with accuracy ranging from 51{\%} to 89{\%}, averaged across all feature groups and languages. Next, we turn to a large-scale investigation of pluralia tantum. Using dictionaries, we extract candidate words for Italian, Russian and English and keep those for which the changing ratio of singular and plural form is evident in a corresponding reference corpus. We use an LLM to annotate each instance from the reference corpora according to the annotation framework. We show that the large amount of automatically annotated sentences for each feature can be used to perform in-depth linguistic analysis. Focusing on the correlation between an annotated feature and the grammatical form (singular vs. plural), patterns of morpho-semantic change are noted."
}
```
