import os
from typing import List, Dict, Any
import matplotlib.pyplot as plt
import pandas as pd

from adaptive_scheduler.engine import SimulationEngine
from adaptive_scheduler.profiles import default_vm_profiles
from adaptive_scheduler.scheduler import AdaptiveScheduler
from adaptive_scheduler.workloads import generate_workload


def run_benchmark(
    scenarios: List[str] = ["light", "medium", "heavy"],
    seed: int = 42,
    custom_job_counts: Dict[str, int] | None = None,
) -> pd.DataFrame:
    """Executes all schedulers across specified scenarios and aggregates performance metrics."""
    records: List[Dict[str, Any]] = []
    baselines = ["fcfs", "round_robin", "min_min", "max_min", "priority"]

    for scenario in scenarios:
        count = custom_job_counts.get(scenario) if custom_job_counts else None
        jobs = generate_workload(scenario, count=count, seed=seed)
        vms = default_vm_profiles()

        # 1. Run Adaptive Scheduler
        engine_adaptive = SimulationEngine(vms)
        scheduler = AdaptiveScheduler()
        metrics_adaptive = engine_adaptive.run_adaptive(jobs, scheduler)
        records.append({
            "scenario": scenario,
            "algorithm": "Adaptive",
            "makespan": metrics_adaptive.makespan,
            "avg_turnaround_time": metrics_adaptive.avg_turnaround_time,
            "avg_waiting_time": metrics_adaptive.avg_waiting_time,
            "deadline_miss_rate": metrics_adaptive.deadline_miss_rate,
            "energy_consumed_kwh": metrics_adaptive.energy_consumed_kwh,
        })

        # 2. Run Baseline Schedulers
        for algo in baselines:
            engine_base = SimulationEngine(vms)
            metrics_base = engine_base.run_baseline(jobs, algo)
            records.append({
                "scenario": scenario,
                "algorithm": algo.replace("_", " ").title(),
                "makespan": metrics_base.makespan,
                "avg_turnaround_time": metrics_base.avg_turnaround_time,
                "avg_waiting_time": metrics_base.avg_waiting_time,
                "deadline_miss_rate": metrics_base.deadline_miss_rate,
                "energy_consumed_kwh": metrics_base.energy_consumed_kwh,
            })

    return pd.DataFrame(records)


def generate_benchmark_plots(df: pd.DataFrame, output_dir: str = "plots") -> None:
    """Generates comparison bar charts for each metric across workload scenarios."""
    os.makedirs(output_dir, exist_ok=True)
    metrics = [
        ("makespan", "Makespan (seconds)", "Makespan Comparison"),
        ("avg_turnaround_time", "Avg Turnaround Time (s)", "Average Turnaround Time"),
        ("avg_waiting_time", "Avg Waiting Time (s)", "Average Waiting Time"),
        ("deadline_miss_rate", "Deadline Miss Rate", "Deadline Miss Rate"),
        ("energy_consumed_kwh", "Energy Consumed (kWh)", "Energy Consumption"),
    ]

    scenarios = df["scenario"].unique()
    for metric, ylabel, title in metrics:
        fig, ax = plt.subplots(figsize=(10, 6))
        pivot_df = df.pivot(index="scenario", columns="algorithm", values=metric)
        pivot_df = pivot_df.reindex(scenarios)

        pivot_df.plot(kind="bar", ax=ax, width=0.8)
        ax.set_title(title, fontsize=14, fontweight="bold")
        ax.set_ylabel(ylabel, fontsize=12)
        ax.set_xlabel("Workload Scenario", fontsize=12)
        ax.grid(axis="y", linestyle="--", alpha=0.7)
        plt.xticks(rotation=0)
        plt.tight_layout()

        file_path = os.path.join(output_dir, f"{metric}_comparison.png")
        plt.savefig(file_path, dpi=300)
        plt.close()