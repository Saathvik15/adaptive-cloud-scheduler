import argparse
import sys
from pathlib import Path
from typing import List, Optional

from adaptive_scheduler.benchmark import generate_benchmark_plots, run_benchmark


def parse_args(args: Optional[List[str]] = None) -> argparse.Namespace:
    """Parse command line arguments for the scheduler simulator."""
    parser = argparse.ArgumentParser(
        description="Adaptive Cloud Job Scheduler Benchmark & Simulation Runner"
    )

    parser.add_argument(
        "--scenarios",
        nargs="+",
        choices=["light", "medium", "heavy"],
        default=["light", "medium", "heavy"],
        help="Workload scenarios to run (default: light medium heavy).",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for reproducible workload generation (default: 42).",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="outputs/evaluation",
        help="Directory path to save benchmark plots and output artifacts (default: outputs/evaluation).",
    )

    return parser.parse_args(args)


def main(args: Optional[List[str]] = None) -> int:
    """CLI entrypoint executing benchmark scenarios and visual generation."""
    parsed = parse_args(args)

    output_path = Path(parsed.output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    print("=== Adaptive Cloud Job Scheduler CLI ===")
    print(f"Scenarios: {', '.join(parsed.scenarios)}")
    print(f"Seed: {parsed.seed}")
    print(f"Output Directory: {output_path.resolve()}\n")

    try:
        print("Running benchmark evaluation...")
        results_df = run_benchmark(scenarios=parsed.scenarios, seed=parsed.seed)
        print("Benchmark complete. Data summary:")
        print(results_df.head())

        print(f"\nGenerating visual comparative plots in '{output_path}'...")
        generate_benchmark_plots(results_df, output_dir=str(output_path))
        print("Plots generated successfully.")

        return 0

    except Exception as e:
        print(f"Error during execution: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
