import os
import pytest
from adaptive_scheduler.benchmark import generate_benchmark_plots, run_benchmark


def test_run_benchmark_small_counts():
    counts = {"light": 10, "medium": 10}
    df = run_benchmark(scenarios=["light", "medium"], seed=42, custom_job_counts=counts)

    assert not df.empty
    assert "Adaptive" in df["algorithm"].values
    assert "Fcfs" in df["algorithm"].values
    assert set(df["scenario"].unique()) == {"light", "medium"}
    assert "makespan" in df.columns
    assert "energy_consumed_kwh" in df.columns


def test_generate_benchmark_plots(tmp_path):
    output_dir = str(tmp_path / "plots")
    counts = {"light": 10}
    df = run_benchmark(scenarios=["light"], seed=42, custom_job_counts=counts)

    generate_benchmark_plots(df, output_dir=output_dir)

    expected_files = [
        "makespan_comparison.png",
        "avg_turnaround_time_comparison.png",
        "avg_waiting_time_comparison.png",
        "deadline_miss_rate_comparison.png",
        "energy_consumed_kwh_comparison.png",
    ]

    for filename in expected_files:
        assert os.path.exists(os.path.join(output_dir, filename))