#!/usr/bin/env python3
"""
Parse LLM outputs across model subdirectories.

Scans all CSV files in each model subfolder, extracts JSON from
output columns (output_1, output_2, output_3, or output_json),
and writes the parsed fields back into the same CSV.

Usage
-----
    python parse_outputs.py --output-dir output/
"""
import os
import logging
import argparse
from pathlib import Path

import pandas as pd
from llm_classifier.parser import Parser


def main():
    p = argparse.ArgumentParser(
        description="Parse LLM outputs in output_<model>/output_<file>.csv"
    )
    p.add_argument(
        "--output-dir",
        required=True,
        help="Base output directory containing one subfolder per model",
    )
    p.add_argument(
        "--report-name",
        default="parsing_report.csv",
        help="Name of the CSV to write the parse failures report",
    )
    args = p.parse_args()

    output_dir = Path(args.output_dir)
    if not output_dir.is_dir():
        raise FileNotFoundError(f"{output_dir} is not a directory")

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")
    parser = Parser(verbose=True)

    failures = []

    for model_dir in sorted(output_dir.iterdir()):
        if not model_dir.is_dir():
            continue
        model_name = model_dir.name
        logging.info(f"=== Processing model: {model_name} ===")

        for csv_path in sorted(model_dir.glob("*.csv")):
            logging.info(f"Parsing file: {csv_path.name}")
            df = pd.read_csv(csv_path)

            # Try standard output columns
            output_cols = [c for c in ("output_1", "output_2", "output_3", "output_json")
                           if c in df.columns]

            if not output_cols:
                logging.warning(f"  No output columns found in {csv_path.name}, skipping")
                continue

            for col in output_cols:
                extracted = df[col].apply(parser.extract_json)

                # Record failures
                failed_idxs = extracted[extracted.isna()].index.tolist()
                for row_idx in failed_idxs:
                    failures.append({
                        "model": model_name,
                        "file": csv_path.name,
                        "column": col,
                        "row": int(row_idx),
                    })

                # Normalize successful parses into new columns
                valid = extracted.dropna()
                if not valid.empty:
                    parsed = pd.json_normalize(valid.tolist())
                    parsed.index = valid.index
                    for key in parsed.columns:
                        df[key] = parsed[key]

            df.to_csv(csv_path, index=False)
            logging.info(f"  ✔ Saved parsed data back to {csv_path.name}")

    # Write failures report
    report_df = pd.DataFrame(failures)
    report_path = output_dir / args.report_name
    report_df.to_csv(report_path, index=False)
    logging.info(f"Parsing failures report: {report_path}")


if __name__ == "__main__":
    main()
