import json
from pathlib import Path
from typing import Dict, Any, Union
import pandas as pd


class PerformanceReporter:
    """Analyzes benchmark DataFrames and computes performance metrics."""

    def __init__(self, results_df: pd.DataFrame):
        self.df = results_df.copy()

    def compute_summary(self) -> Dict[str, Any]:
        """Calculate percentage improvements of Adaptive Scheduler vs baseline average."""
        if self.df.empty:
            return {}

        metrics = ["makespan", "turnaround_time", "waiting_time", "deadline_miss_rate", "energy_kwh"]
        summary: Dict[str, Any] = {}

        for scenario in self.df["scenario"].unique():
            scen_df = self.df[self.df["scenario"] == scenario]
            adaptive_row = scen_df[scen_df["algorithm"] == "Adaptive"]
            baseline_rows = scen_df[scen_df["algorithm"] != "Adaptive"]

            if adaptive_row.empty or baseline_rows.empty:
                continue

            scen_summary: Dict[str, float] = {}
            for metric in metrics:
                if metric in scen_df.columns:
                    adapt_val = float(adaptive_row[metric].values[0])
                    base_avg = float(baseline_rows[metric].mean())

                    if base_avg != 0:
                        improvement = ((base_avg - adapt_val) / base_avg) * 100.0
                    else:
                        improvement = 0.0

                    scen_summary[f"{metric}_reduction_pct"] = round(improvement, 2)

            summary[scenario] = scen_summary

        return summary

    def export_json(self, filepath: Union[str, Path]) -> None:
        """Export calculated summary stats to a JSON file."""
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        summary = self.compute_summary()
        with open(path, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=4)

    def export_markdown(self, filepath: Union[str, Path]) -> None:
        """Export benchmark summary as formatted Markdown tables."""
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        summary = self.compute_summary()

        md_lines = ["# Performance Reporter Summary\n"]
        for scenario, metrics in summary.items():
            md_lines.append(f"## Scenario: {scenario.capitalize()}")
            md_lines.append("| Metric | Adaptive Improvement (%) |")
            md_lines.append("| --- | --- |")
            for metric_name, val in metrics.items():
                formatted_name = metric_name.replace("_reduction_pct", "").replace("_", " ").title()
                md_lines.append(f"| {formatted_name} | {val}% |")
            md_lines.append("")

        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(md_lines))
