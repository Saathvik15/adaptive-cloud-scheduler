\# System Architecture \& Technical Specifications



\## Architectural Overview



The Adaptive Cloud Job Scheduler simulates and benchmarks cloud scheduling heuristics against heterogeneous workloads.



```mermaid

graph TD

&#x20;   A\[Workload Generator] -->|Synthetic Jobs| B\[Workload Analyzer]

&#x20;   B -->|Resource \& Slack Profile| C\[Adaptive Scheduler]

&#x20;   B -->|Original Jobs| D\[Baseline Schedulers]

&#x20;   C -->|Dynamic Allocation| E\[Simulation Engine]

&#x20;   D -->|FCFS / RR / MinMin / MaxMin / Priority| E

&#x20;   E -->|Execution Metrics| F\[Benchmarking \& Plot Engine]

&#x20;   E -->|SLA \& Runtime Data| G\[Performance Reporter Engine]

&#x20;   G -->|Summary JSON / Markdown| H\[Outputs \& Artifacts]

&#x20;   F -->|PNG Plots| H


Component Breakdowns
1. Workload Analyzer (analyzer.py)
Classifies arriving jobs based on early execution measurements (first 10% sample) into 5 resource categories:

CPU_INTENSIVE

MEMORY_INTENSIVE

IO_HEAVY

BALANCED

DEADLINE_CRITICAL

2. Adaptive Scheduler Engine (scheduler.py)
Computes normalized dynamic suitability scores for every candidate VM:

Score = 0.4 * Utilization_Match + 0.3 * Available_Resources + 0.2 * Historical_Performance + 0.1 * Energy_Efficiency

3. Discrete-Event Simulator (engine.py)
Executes workload allocations, tracking job execution cycles, VM busy times, energy consumption (kWh), and deadline miss rates.

4. Baseline Schedulers (baselines.py)
Provides deterministic heuristic baselines:

First-Come, First-Served (FCFS)

Round Robin (RR)

Min-Min

Max-Min

Priority-Based

5. Performance Reporter Engine (reporter.py)
Aggregates simulation DataFrames, calculating relative percentage savings for makespan, turnaround time, waiting time, deadline miss rate, and energy consumption.
'@ | Out-File -FilePath "docs/architecture.md" -Encoding utf8
