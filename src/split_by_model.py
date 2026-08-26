"""
Split the consolidated results file into one JSONL file per model, so you
have a clean, standalone dataset for each model tested (e.g.
results/by_model/gemini-3.6-flash.jsonl, results/by_model/gpt-4o.jsonl)
in addition to the single merged consolidated_responses.jsonl.

Usage:
    python3 src/split_by_model.py
    # reads results/consolidated_responses.jsonl by default,
    # writes results/by_model/<model_name>.jsonl for each model present

    python3 src/split_by_model.py --input results/consolidated_responses.jsonl --out-dir results/by_model
"""
import argparse
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
    ap.add_argument("--input", default="results/consolidated_responses.jsonl")
    ap.add_argument("--out-dir", default="results/by_model")
    args = ap.parse_args()

    rows = load_jsonl(args.input)
    if not rows:
        print(f"No rows found in {args.input}")
        return

    by_model: dict[str, list] = {}
    for row in rows:
        model_name = row.get("model_name", "unknown")
        by_model.setdefault(model_name, []).append(row)

    os.makedirs(args.out_dir, exist_ok=True)

    print(f"Splitting {len(rows)} total rows across {len(by_model)} model(s):\n")
    for model_name, model_rows in sorted(by_model.items()):
        # sort by scenario_id for readability/consistency
        model_rows.sort(key=lambda r: r.get("scenario_id", ""))
        out_path = os.path.join(args.out_dir, f"{model_name}.jsonl")
        with open(out_path, "w") as f:
            for row in model_rows:
                f.write(json.dumps(row) + "\n")
        print(f"  {model_name}: {len(model_rows)} scenarios -> {out_path}")


if __name__ == "__main__":
    main()