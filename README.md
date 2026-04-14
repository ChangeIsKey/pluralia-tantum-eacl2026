# Elections go bananas: A First Large-scale Multilingual Study of Pluralia Tantum using LLMs

[![Paper](https://img.shields.io/badge/Paper-EACL%202026-blue)](https://aclanthology.org/2026.eacl-long.308/)
[![License](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey)](https://creativecommons.org/licenses/by/4.0/)

> Elena Spaziani, Kamyar Zeinalipour, Pierluigi Cassotti, Nina Tahmasebi
>
> *Proceedings of the 19th Conference of the European Chapter of the Association for Computational Linguistics (EACL 2026), Rabat, Morocco*

## Overview

**Pluralia tantum** are defective nouns that lack a singular form (e.g., *scissors*, *trousers*, *elections*). This paper presents the first large-scale, multilingual study of how pluralia tantum evolve in meaning across **Italian**, **Russian**, and **English**, using Large Language Models as automated annotators.

We introduce `llm_classifier`, a modular toolkit for:

1. **Annotating** corpus instances of pluralia tantum according to *Lexicalization Profiles* — a framework capturing sense inventory, sense relations (primary, metaphoric, metonymic, taxonomic), semantic features, morphological case, colligations, register, and text theme.
2. **Evaluating** LLM annotation quality against hand-annotated gold standards using Exact Match Accuracy, Jaccard Similarity, and Micro-F1 scores.
3. **Visualizing** cross-model and cross-language results with publication-quality plots.

### Key Findings

- OpenAI and DeepSeek models achieve **51%–89% accuracy** averaged across all feature groups and languages, making them viable annotators for large-scale linguistic studies.
- Using dictionaries, we extract candidate pluralia tantum words and retain those where the **singular/plural ratio shift** is evident in reference corpora.
- Automatically annotated data reveals **patterns of morpho-semantic change** — correlations between annotated features and grammatical form (singular vs. plural) that would be infeasible to discover through manual annotation alone.

## Repository Structure

```
├── llm_classifier/          # Core Python package
│   ├── core.py              # Annotator: multi-model LLM annotation with resume
│   ├── parser.py            # Parser: robust JSON extraction from LLM outputs
│   ├── evaluator.py         # Evaluator: multi-label metrics computation
│   └── cli.py               # Command-line interface
├── evaluate.py              # Batch evaluation across datasets and models
├── parse_outputs.py         # Batch JSON parsing of raw LLM outputs
├── plot_results.py          # Publication-quality bar chart generation
├── config/                  # Prompt templates (system messages, zero/few-shot)
├── data/                    # Input datasets (per-language CSVs)
├── english/                 # English-specific data
├── italian/                 # Italian-specific data
├── russian/                 # Russian-specific data
└── src/                     # Additional analysis scripts
```

## Installation

```bash
pip install openai pandas scikit-learn numpy matplotlib seaborn
```

## Annotation Framework

The annotation follows the **Lexicalization Profiles** framework with the following categories:

| Category | Description | Example Values |
|----------|-------------|----------------|
| **Sense Inventory** | Which meaning of the word is used | `1.01` (general talk), `2.01` (formal discussion), `3.01` (censure) |
| **Sense Categories** | Semantic derivation mechanism | `primary`, `metaphoric`, `metonymic`, `taxonomic` |
| **Semantic Categories** | Concreteness and animacy | `[abstract, inanimate]` |
| **Morphological Categories** | Grammatical case | `nominative`, `genitive`, `dative`, etc. |
| **Colligation L1/R1** | POS of adjacent words | `noun`, `verb`, `preposition`, etc. |
| **Diaphasic Preference** | Register level | `neutral`, `specialized` |
| **Text Theme** | Thematic domain of the source text | `politics`, `law`, `daily life`, `literature`, etc. |

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

If you use this code or data, please cite our paper:

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
}
```

## License

This work is licensed under a [Creative Commons Attribution 4.0 International License](https://creativecommons.org/licenses/by/4.0/).
