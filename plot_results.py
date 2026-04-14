#!/usr/bin/env python3
"""
Plotting script for evaluation results.

Generates publication-quality bar plots (PDF + PNG) comparing model
performance across annotation categories, optionally grouped by language.

Usage
-----
    # Single-language or averaged plot
    python plot_results.py --input evaluations/summary_by_model_label.csv

    # Per-language plots (requires a language mapping)
    python plot_results.py --input evaluations/all_datasets_evaluated.csv --by-language

    # Custom metric
    python plot_results.py --input evaluations/summary_by_model_label.csv --metric f1_micro
"""
import os
import argparse
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # non-interactive backend for servers
import matplotlib.pyplot as plt
import seaborn as sns


# ─── Pretty label mapping ────────────────────────────────────────────────────
PRETTY_MAP = {
    "sense_inventory":          "Sense Inventory",
    "sense_categories":         "Sense Categories",
    "semantic_categories":      "Semantic Categories",
    "morphological_categories": "Morphological Categories",
    "colligation_L1":           "Colligation L1",
    "colligation_R1":           "Colligation R1",
    "diaphasic_preference":     "Diaphasic Preference",
    "text_theme":               "Text Theme",
}

LABEL_ORDER = list(PRETTY_MAP.values())


# ─── Helpers ──────────────────────────────────────────────────────────────────
def shorten_model_name(name: str) -> str:
    """Keep text up to the second dash (e.g. chatgpt-4o-latest → chatgpt-4o)."""
    parts = name.split("-")
    return "-".join(parts[:2]) if len(parts) >= 3 else name


def _bar_plot(df_plot: pd.DataFrame, metric: str, title: str,
              out_dir: str, filename: str):
    """Draw a single bar plot and save it as PDF + PNG."""
    df_plot = df_plot.copy()
    df_plot["label_pretty"] = df_plot["label"].map(PRETTY_MAP)
    df_plot = df_plot.dropna(subset=["label_pretty"])

    order = [l for l in LABEL_ORDER if l in df_plot["label_pretty"].values]
    if not order:
        print(f"  [SKIP] No matching labels for {title}")
        return

    sns.set_theme(style="whitegrid", font_scale=1.6)
    palette = sns.color_palette("tab10", n_colors=df_plot["model"].nunique())
    plt.rcParams.update({
        "axes.titlesize": 22, "axes.labelsize": 20,
        "xtick.labelsize": 16, "ytick.labelsize": 16,
    })

    fig, ax = plt.subplots(figsize=(20, 8))
    sns.barplot(
        data=df_plot,
        x="label_pretty",
        y=metric,
        hue="model",
        order=order,
        palette=palette,
        edgecolor="black",
        ax=ax,
        errorbar=None,
    )

    # Percentage labels on bars
    for p in ax.patches:
        pct = p.get_height() * 100
        if pct > 0:
            ax.annotate(
                f"{pct:.0f}",
                (p.get_x() + p.get_width() / 2, p.get_height()),
                ha="center", va="bottom",
                fontsize=11,
                xytext=(0, 4), textcoords="offset points",
            )

    ax.set_title(title)
    ax.set_xlabel("Label")
    ax.set_ylabel(metric.replace("_", " ").title())
    ax.set_ylim(0, 1.05)
    ax.tick_params(axis="x", rotation=30)

    # Legend
    handles, labels = ax.get_legend_handles_labels()
    if ax.get_legend() is not None:
        ax.get_legend().remove()
    labels_short = [shorten_model_name(l) for l in labels]
    fig.legend(
        handles, labels_short,
        loc="upper center",
        ncol=min(len(labels_short), 8),
        frameon=False,
        bbox_to_anchor=(0.5, 1.02),
    )

    fig.tight_layout(rect=[0, 0, 1, 0.96])

    os.makedirs(out_dir, exist_ok=True)
    for ext in ("pdf", "png"):
        path = os.path.join(out_dir, f"{filename}.{ext}")
        fig.savefig(path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"  ✔ Saved: {out_dir}/{filename}.[pdf|png]")


# ─── Main plotting functions ─────────────────────────────────────────────────
def plot_summary(input_csv: str, metric: str, out_dir: str):
    """Plot from summary_by_model_label.csv (one plot, all languages averaged)."""
    df = pd.read_csv(input_csv)
    df = df[~df["model"].str.contains("checkpoint", case=False, na=False)]

    if df.empty:
        print("[WARN] No data to plot after filtering.")
        return

    _bar_plot(df, metric, f"{metric.replace('_', ' ').title()} (All Languages)",
              out_dir, f"barplot_{metric}")

    # Print average metrics per model
    metric_cols = [c for c in df.columns
                   if c in ("exact_match_accuracy", "jaccard_score",
                            "precision_micro", "recall_micro", "f1_micro")]
    avg = df.groupby("model")[metric_cols].mean().sort_values(
        by=metric, ascending=False
    )
    print(f"\n=== Average Metrics by Model ({metric}) ===")
    print(avg.to_string())


def plot_by_language(input_csv: str, metric: str, out_dir: str,
                     lang_map: dict = None):
    """
    Plot from all_datasets_evaluated.csv, one plot per language.

    Parameters
    ----------
    lang_map : dict
        Maps dataset name → language label. If None, each dataset is
        treated as its own group.
    """
    df = pd.read_csv(input_csv)
    df = df[~df["model"].str.contains("checkpoint", case=False, na=False)]

    if lang_map:
        df["language"] = df["data"].map(lang_map).fillna("unknown")
    else:
        df["language"] = df["data"]

    metric_cols = [c for c in df.columns
                   if c in ("exact_match_accuracy", "jaccard_score",
                            "precision_micro", "recall_micro", "f1_micro")]

    grouped = (
        df.groupby(["language", "label", "model"])[metric_cols]
        .mean()
        .reset_index()
    )

    for lang in sorted(grouped["language"].unique()):
        df_lang = grouped[grouped["language"] == lang]
        _bar_plot(df_lang, metric, f"{metric.replace('_', ' ').title()} — {lang}",
                  out_dir, f"barplot_{metric}_{lang}")

        # Per-language summary
        avg = df_lang.groupby("model")[metric_cols].mean().sort_values(
            by=metric, ascending=False
        )
        print(f"\n=== [{lang}] Average Metrics by Model ===")
        print(avg.to_string())


def main():
    parser = argparse.ArgumentParser(
        description="Plot evaluation results as publication-quality bar charts"
    )
    parser.add_argument("--input", required=True,
                        help="Evaluation CSV (summary_by_model_label.csv or all_datasets_evaluated.csv)")
    parser.add_argument("--metric", default="jaccard_score",
                        choices=["jaccard_score", "exact_match_accuracy",
                                 "f1_micro", "precision_micro", "recall_micro"],
                        help="Metric to plot (default: jaccard_score)")
    parser.add_argument("--output-dir", default="figs",
                        help="Directory to save figures (default: figs)")
    parser.add_argument("--by-language", action="store_true",
                        help="Generate per-language plots (requires language mapping)")
    parser.add_argument("--lang-map", default=None,
                        help="JSON file mapping dataset names to languages")
    args = parser.parse_args()

    if args.by_language:
        lang_map = None
        if args.lang_map:
            import json
            with open(args.lang_map) as f:
                lang_map = json.load(f)
        plot_by_language(args.input, args.metric, args.output_dir, lang_map)
    else:
        plot_summary(args.input, args.metric, args.output_dir)


if __name__ == "__main__":
    main()
