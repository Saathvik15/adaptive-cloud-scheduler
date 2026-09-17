# Adaptive Cloud Scheduler

An event-driven simulation framework for dynamic cloud job scheduling across heterogeneous VM infrastructure. Evaluates multi-objective performance (Makespan, Turnaround Time, Waiting Time, Deadline Miss Rates, Energy Consumption) against 5 standard baseline heuristics: FCFS, Round Robin, Min-Min, Max-Min, and Priority.

---

## Quick Start & Installation
```powershell
# 1. Activate Virtual Environment
.\.venv\Scripts\Activate.ps1

# 2. Install Editable Package
pip install -e .
python -m adaptive_scheduler.main --scenarios light medium heavy --seed 42 --output-dir outputs/evaluation
python -m pytest tests/ -v
