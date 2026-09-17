# Adaptive Cloud Scheduler - System Architecture

## High-Level Data Flow
## Module Directory & Responsibilities

* **`models.py`**: Core dataclasses (`Job`, `VMProfile`, `ResourceGroup`, `AssignmentResult`).
* **`profiles.py`**: Standard hardware profiles (`Compute`, `Eco`, `Memory`, `Small`).
* **`analyzer.py`**: Workload categorizer evaluating core-to-memory ratios and deadline slack.
* **`scheduler.py`**: Adaptive multi-factor heuristic scoring engine balancing CPU, memory, power, and deadlines.
* **`baselines.py`**: Standard baseline heuristics (FCFS, Round Robin, Min-Min, Max-Min, Priority).
* **`workloads.py`**: Deterministic bimodal workload generator for `light`, `medium`, and `heavy` scenarios.
* **`engine.py`**: Discrete-event execution engine calculating makespan, turnaround times, wait times, deadline miss rates, and energy usage (kWh).
* **`benchmark.py`**: Cross-algorithm matrix evaluator and plot renderer.
* **`reporter.py`**: Relative percentage improvement summary compiler and JSON exporter.
* **`main.py`**: Terminal entrypoint managing flags and execution flow.
