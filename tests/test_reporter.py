import pytest
import json
import pandas as pd
from pathlib import Path
from adaptive_scheduler.reporter import PerformanceReporter


@pytest.fixture
def sample_benchmark_df():
    data = [
        {"scenario": "light", "algorithm": "Adaptive", "makespan": 80.0, "waiting_time": 10.0, "turnaround_time": 90.0, "deadline_miss_rate": 0.05, "energy_kwh": 15.0},
        {"scenario": "light", "algorithm": "FCFS", "makespan": 100.0, "waiting_time": 20.0, "turnaround_time": 120.0, "deadline_miss_rate": 0.15, "energy_kwh": 20.0},
        {"scenario": "light", "algorithm": "RR", "makespan": 100.0, "waiting_time": 20.0, "turnaround_time": 120.0, "deadline_miss_rate": 0.15, "energy_kwh": 20.0},
    ]
    return pd.DataFrame(data)


def test_reporter_compute_summary(sample_benchmark_df):
    reporter = PerformanceReporter(sample_benchmark_df)
    summary = reporter.compute_summary()

    assert "light" in summary
    assert summary["light"]["makespan_reduction_pct"] == 20.0
    assert summary["light"]["waiting_time_reduction_pct"] == 50.0


def test_reporter_export_files(sample_benchmark_df, tmp_path):
    reporter = PerformanceReporter(sample_benchmark_df)
    json_path = tmp_path / "summary.json"
    md_path = tmp_path / "summary.md"

    reporter.export_json(json_path)
    reporter.export_markdown(md_path)

    assert json_path.exists()
    assert md_path.exists()

    with open(json_path) as f:
        data = json.load(f)
        assert "light" in data
