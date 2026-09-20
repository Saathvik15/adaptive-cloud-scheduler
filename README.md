# Adaptive Cloud Job Scheduler

An OS course assignment delivering a discrete-event simulation framework designed to evaluate an dynamic, multi-objective **Adaptive Cloud Scheduler** against five baseline scheduling heuristics across heterogeneous cloud workloads.

---

## 📸 Executive Summary & Key Results

The Adaptive Cloud Scheduler balances core-to-memory ratios, task deadlines, and VM energy consumption profiles. Across benchmark evaluations:

* **Energy Reduction:** Cuts energy consumption by **~50%** ($0.004562\text{ kWh}$ vs $0.009162\text{ kWh}$ for FCFS).
* **Deadline Adherence:** Maintains a **0.0% deadline miss rate** under normal load conditions[cite: 5].
* **Latency Optimization:** Keeps turnaround and waiting times lower than Max-Min and Priority heuristics while preventing queue starvation.

---

## 🏗️ Architecture & Simulation Pipeline

```mermaid
flowchart TD
    A[Workload Generator] -->|Synthetic Bimodal Jobs| B[Workload Analyzer]
    B -->|Dominant Resource & Slack| C{Scheduler Selection}
    C -->|Adaptive Scoring| D[Adaptive Scheduler]
    C -->|FCFS / RR / MinMin / MaxMin / Priority| E[Baseline Schedulers]
    D --> F[Discrete-Event Simulation Engine]
    E --> F
    F --> G[Benchmarking Engine]
    G --> H[Matplotlib Plots]
    G --> I[Pandas Data Summary]