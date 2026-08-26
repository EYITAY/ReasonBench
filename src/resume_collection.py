"""
Resume a partial collection run by skipping scenarios that already have a
response for the given model in an existing results file.

Why this exists: Gemini's free tier caps at ~20 requests/day, so a full
26-scenario run often gets cut off partway through by a 429 quota error.
Re-running from scratch would waste quota re-doing scenarios you already
have clean data for. This script finds what's already done and runs only
what's left.

Usage:
    python3 src/resume_collection.py \\
        --model gemini-3.6-flash \\
        --scenarios data/scenarios.jsonl \\
        --previous-results results/responses_20260823T113738Z.jsonl

    # Then feed the printed list into run_collection.py, or use --run to
    # have this script call run_collection.py directly on just the
    # remaining scenarios.

    python3 src/resume_collection.py \\
        --model gemini-3.6-flash \\
        --previous-results results/responses_20260823T113738Z.jsonl \\
        --run
"""
import argparse
import json
import os
import subprocess
import sys


def load_jsonl(path):
    rows = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def completed_scenario_ids(results_paths, model_name):
    """Returns the set of scenario_ids that already have a response for
    model_name across one or more results files (so you can point this at
    several partial runs from different days if needed)."""
    done = set()
    for path in results_paths:
        for row in load_jsonl(path):
            if row.get("model_name") == model_name and row.get("scenario_id"):
                done.add(row["scenario_id"])
    return done


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True, help="Friendly model name, e.g. gemini-3.6-flash")
    ap.add_argument("--scenarios", default="data/scenarios.jsonl")
    ap.add_argument("--previous-results", nargs="+", required=True,
                     help="One or more results/responses_*.jsonl files to check for already-completed scenarios")
    ap.add_argument("--out", default="data/scenarios_remaining.jsonl",
                     help="Where to write the filtered scenario file containing only what's left to run")
    ap.add_argument("--run", action="store_true",
                     help="After filtering, immediately invoke run_collection.py on the remaining scenarios")
    ap.add_argument("--temperature", type=float, default=0.7)
    args = ap.parse_args()

    all_scenarios = load_jsonl(args.scenarios)
    done_ids = completed_scenario_ids(args.previous_results, args.model)

    remaining = [s for s in all_scenarios if s["scenario_id"] not in done_ids]

    print(f"Total scenarios: {len(all_scenarios)}")
    print(f"Already completed for {args.model}: {len(done_ids)} -> {sorted(done_ids)}")
    print(f"Remaining: {len(remaining)} -> {[s['scenario_id'] for s in remaining]}")

    if not remaining:
        print("Nothing left to run -- all scenarios already have a response for this model.")
        return

    with open(args.out, "w") as f:
        for s in remaining:
            f.write(json.dumps(s) + "\n")
    print(f"Wrote remaining scenarios to {args.out}")

    if args.run:
        print(f"\nInvoking run_collection.py on remaining scenarios...")
        cmd = [
            sys.executable,
            os.path.join(os.path.dirname(__file__), "run_collection.py"),
            "--scenarios", args.out,
            "--models", args.model,
            "--temperature", str(args.temperature),
        ]
        subprocess.run(cmd, check=False)
    else:
        print(f"\nTo run just these scenarios:\n"
              f"  python3 src/run_collection.py --scenarios {args.out} --models {args.model}")


if __name__ == "__main__":
    main()