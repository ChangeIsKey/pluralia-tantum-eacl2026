#!/usr/bin/env python3
"""
Batch evaluation script.

Evaluates LLM predictions against ground-truth CSV files and produces:
  - Per-dataset evaluation CSVs
  - A combined evaluation CSV across all datasets
  - A summary CSV averaged by model & label

Usage
-----
    python evaluate.py --data data/ --predictions output/ --output evaluations/
"""
import os
import glob
import argparse
import pandas as pd
from llm_classifier.evaluator import Evaluator


def evaluate_all(data_folder: str, predictions_folder: str, output_folder: str):
    """
    Batch-evaluate predictions against multiple ground-truth CSVs.

    Parameters
    ----------
    data_folder : str
        Directory containing ground-truth CSV files (*.csv).
    predictions_folder : str
        Directory containing subfolders per model, each with
        ``output_<dataset>.csv`` files.
    output_folder : str
        Directory where evaluation results will be saved.
    """
    ev = Evaluator()
    all_results = []

    os.makedirs(output_folder, exist_ok=True)

    for gt_path in sorted(glob.glob(os.path.join(data_folder, "*.csv"))):
        dataset_name = os.path.splitext(os.path.basename(gt_path))[0]
        dataset_records = []

        for model_name in sorted(os.listdir(predictions_folder)):
            model_dir = os.path.join(predictions_folder, model_name)
            if not os.path.isdir(model_dir):
                continue

            pred_file = os.path.join(model_dir, f"output_{dataset_name}.csv")
            if not os.path.exists(pred_file):
                print(f"[WARN] Missing: {model_name}/output_{dataset_name}.csv")
                continue

            df_pred = pd.read_csv(pred_file)
            metrics_df = ev.evaluate(df_pred, ground_truth_path=gt_path)

            metrics_df = metrics_df.reset_index().rename(columns={"index": "label"})
            metrics_df["model"] = model_name
            metrics_df["data"] = dataset_name

            dataset_records.append(metrics_df)

        if dataset_records:
            df_dataset = pd.concat(dataset_records, ignore_index=True)
            out_path = os.path.join(output_folder, f"{dataset_name}_evaluated.csv")
            df_dataset.to_csv(out_path, index=False)
            print(f"✔ Saved: {out_path}")
            all_results.append(df_dataset)

    if not all_results:
        print("[WARN] No evaluation results produced.")
        return

    # Combined results
    df_all = pd.concat(all_results, ignore_index=True)
    df_all.to_csv(os.path.join(output_folder, "all_datasets_evaluated.csv"), index=False)

    # Summary averaged by model & label
    metric_cols = [
        "exact_match_accuracy",
        "jaccard_score",
        "precision_micro",
        "recall_micro",
        "f1_micro",
    ]
    available = [m for m in metric_cols if m in df_all.columns]

    summary = df_all.groupby(["model", "label"], as_index=False)[available].mean()
    summary_path = os.path.join(output_folder, "summary_by_model_label.csv")
    summary.to_csv(summary_path, index=False)
    print(f"✔ Summary: {summary_path}")


def main():
    parser = argparse.ArgumentParser(description="Batch evaluation of LLM predictions")
    parser.add_argument("--data", required=True, help="Ground-truth CSV directory")
    parser.add_argument("--predictions", required=True, help="Predictions directory (subfolders per model)")
    parser.add_argument("--output", default="evaluations", help="Output directory for results")
    args = parser.parse_args()
    evaluate_all(args.data, args.predictions, args.output)


if __name__ == "__main__":
    main()
