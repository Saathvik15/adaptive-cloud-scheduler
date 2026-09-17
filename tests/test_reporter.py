import pandas as pd
import pytest
from adaptive_scheduler.reporter import PerformanceReporter


@pytest.fixture
def sample_df():
    data = [
        {
            "scenario": "light",
            "algorithm": "adaptive",
            "makespan": 80.0,
            "avg_turnaround_time": 10.0,
            "avg_waiting_time": 5.0,
            "deadline_miss_rate": 0.05,
            "energy_consumed_kwh": 2.0,
        },
        {
            "scenario": "light",
            "algorithm": "fcfs",
            "makespan": 100.0,
            "avg_turnaround_time": 20.0,
            "avg_waiting_time": 10.0,
            "deadline_miss_rate": 0.10,
            "energy_consumed_kwh": 4.0,
        },
        {
            "scenario": "light",
            "algorithm": "round_robin",
            "makespan": 100.0,
            "avg_turnaround_time": 20.0,
            "avg_waiting_time": 10.0,
            "deadline_miss_rate": 0.10,
            "energy_consumed_kwh": 4.0,
        },
    ]
    return pd.DataFrame(data)


def test_generate_summary(sample_df):
    reporter = PerformanceReporter(sample_df)
    summary = reporter.generate_summary()

    assert "light" in summary
    assert summary["light"]["makespan"]["improvement_pct"] == 20.0
    assert summary["light"]["avg_turnaround_time"]["improvement_pct"] == 50.0


def test_export_json_and_markdown(sample_df, tmp_path):
    reporter = PerformanceReporter(sample_df)
    json_path = tmp_path / "benchmark_summary.json"
    reporter.export_json(str(json_path))

    assert json_path.exists()

    md_table = reporter.to_markdown_table()
    assert "| Scenario | Metric |" in md_table
    assert "light" in md_table
