"""
Consolidate all raw results/responses_*.jsonl files into a single,
de-duplicated file for analysis -- without touching or deleting the original
timestamped files, which remain as the permanent, per-run audit trail.

Why this exists: run_collection.py writes a new timestamped file every
invocation (by design -- it never overwrites a previous run). Combined with
hitting API rate limits mid-run, this can leave your data scattered across
several partial files. This script merges them into one clean file for
actual annotation/classification work, keeping only the most recent response
for any (scenario_id, model_name) pair if it appears more than once.

Usage:
    python3 src/consolidate_results.py
    # scans results/responses_*.jsonl by default, writes
    # results/consolidated_responses.jsonl

    python3 src/consolidate_results.py --results-dir results --out results/consolidated_responses.jsonl
"""
import argparse
import glob
import json
import os


def load_jsonl(path):
    rows = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--results-dir", default="results",
                     help="Directory containing responses_*.jsonl files (default: results/)")
    ap.add_argument("--out", default=None,
                     help="Output path (default: <results-dir>/consolidated_responses.jsonl)")
    args = ap.parse_args()

    out_path = args.out or os.path.join(args.results_dir, "consolidated_responses.jsonl")

    pattern = os.path.join(args.results_dir, "responses_*.jsonl")
    files = sorted(glob.glob(pattern))  # sorted by filename -- timestamps sort chronologically
    # Exclude the output file itself if re-running and it happens to match the glob
    files = [f for f in files if os.path.abspath(f) != os.path.abspath(out_path)]

    if not files:
        print(f"No files found matching {pattern}")
        return

    print(f"Found {len(files)} raw results file(s):")
    for f in files:
        print(f"  - {f}")

    # Key by (scenario_id, model_name) -- later files (later timestamps, since
    # we sorted chronologically) overwrite earlier ones, so the most recent
    # response for a given scenario+model wins if it appears more than once.
    merged: dict[tuple, dict] = {}
    empty_files = []
    total_rows_seen = 0

    for path in files:
        rows = load_jsonl(path)
        if not rows:
            empty_files.append(path)
            continue
        for row in rows:
            total_rows_seen += 1
            key = (row.get("scenario_id"), row.get("model_name"))
            merged[key] = row  # later file wins on duplicate key

    with open(out_path, "w") as f:
        for row in merged.values():
            f.write(json.dumps(row) + "\n")

    print(f"\nTotal rows across all files: {total_rows_seen}")
    print(f"Empty files skipped: {len(empty_files)}")
    print(f"Unique (scenario_id, model_name) pairs after de-duplication: {len(merged)}")
    print(f"Wrote consolidated file to: {out_path}")

    # Quick per-model summary
    by_model: dict[str, int] = {}
    for (scenario_id, model_name) in merged:
        by_model[model_name] = by_model.get(model_name, 0) + 1
    print("\nScenarios completed per model:")
    for model_name, count in sorted(by_model.items()):
        print(f"  {model_name}: {count}/26")


if __name__ == "__main__":
    main()