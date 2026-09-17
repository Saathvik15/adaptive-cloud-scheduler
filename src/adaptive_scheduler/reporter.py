import json
from typing import Dict, Any
import pandas as pd


class PerformanceReporter:
    """Analyzes benchmark DataFrames and generates relative performance metrics."""

    def __init__(self, df: pd.DataFrame):
        self.df = df

    def generate_summary(self) -> Dict[str, Any]:
        metrics = [
            "makespan",
            "avg_turnaround_time",
            "avg_waiting_time",
            "deadline_miss_rate",
            "energy_consumed_kwh",
        ]
        summary = {}
        scenarios = self.df["scenario"].unique()

        for scenario in scenarios:
            scen_df = self.df[self.df["scenario"] == scenario]
            adaptive_row = scen_df[scen_df["algorithm"] == "adaptive"]
            baselines_df = scen_df[scen_df["algorithm"] != "adaptive"]

            if adaptive_row.empty or baselines_df.empty:
                continue

            scen_summary = {}
            for metric in metrics:
                if metric in scen_df.columns:
                    adapt_val = float(adaptive_row[metric].values[0])
                    base_avg = float(baselines_df[metric].mean())

                    if base_avg != 0:
                        pct_imp = ((base_avg - adapt_val) / base_avg) * 100.0
                    else:
                        pct_imp = 0.0

                    scen_summary[metric] = {
                        "adaptive": adapt_val,
                        "baseline_avg": base_avg,
                        "improvement_pct": round(pct_imp, 2),
                    }
            summary[scenario] = scen_summary

        return summary

    def export_json(
        self, filepath: str = "outputs/evaluation/benchmark_summary.json"
    ) -> None:
        summary = self.generate_summary()
        with open(filepath, "w") as f:
            json.dump(summary, f, indent=4)

    def to_markdown_table(self) -> str:
        summary = self.generate_summary()
        lines = [
            "| Scenario | Metric | Adaptive | Baseline Avg | Improvement (%) |",
            "|---|---|---|---|---|",
        ]
        for scenario, metrics in summary.items():
            for metric, vals in metrics.items():
                lines.append(
                    f"| {scenario} | {metric} | {vals['adaptive']:.2f} | {vals['baseline_avg']:.2f} | {vals['improvement_pct']:.2f}% |"
                )
        return "\n".join(lines)
