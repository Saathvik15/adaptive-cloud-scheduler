# Adaptive Cloud Job Scheduler — Implementation Brief

## Role and outcome

You are implementing a research prototype named **Adaptive Cloud Job Scheduler**. Build a runnable, well-tested Python application that simulates cloud-job scheduling and compares an adaptive scheduler against five baseline algorithms.

The system must support repeatable experiments under three workload scenarios and report eight performance metrics. Design it so a future CloudSim Plus (Java) integration can replace the local simulation engine without changing scheduler logic.

## Important technical decision

CloudSim Plus is a Java framework. Do **not** pretend it is a normal Python dependency. Build the scheduler, workloads, metrics, evaluation harness, and charts in Python. Keep any CloudSim Plus connection isolated behind an adapter interface. A Java bridge may be added later.

## Technology stack

- Python 3.11+ (Python 3.14 is available locally)
- PyCharm
- Poetry preferred for dependency management; `requirements.txt` acceptable as a fallback
- NumPy, Pandas, Matplotlib
- pytest and pytest-cov
- Ruff (optional linting)
- GitHub Actions for test CI

## Repository and Git workflow

Use this structure:

```text
adaptive-cloud-scheduler/
├── src/adaptive_scheduler/
│   ├── __init__.py
│   ├── models.py
│   ├── analyzer.py
│   ├── scheduler.py
│   ├── load_balancer.py
│   ├── feedback.py
│   ├── baselines.py
│   ├── workloads.py
│   ├── metrics.py
│   ├── engine.py
│   ├── experiments.py
│   ├── visualization.py
│   ├── simulation.py
│   └── main.py
├── tests/
├── outputs/
├── docs/
├── .github/workflows/tests.yml
├── pyproject.toml
├── README.md
└── .gitignore
```

Team conventions:

- `main` is stable and merged weekly.
- Each of the three team members uses a focused feature branch, for example `feature/vm-profiles`, `feature/adaptive-scheduler`, or `feature/evaluation`.
- Every feature requires unit tests before merging.
- Do not commit `.venv`, `__pycache__`, `.idea`, raw output files, or credentials.

## Domain model

### Resource groups

Implement `ResourceGroup` with exactly five values:

1. `CPU_INTENSIVE`
2. `MEMORY_INTENSIVE`
3. `IO_HEAVY`
4. `BALANCED`
5. `DEADLINE_CRITICAL`

### Job

Create a dataclass with at least:

- `id: str`
- `length_mi: float` — work amount in million instructions
- `required_cores: int`
- `required_memory_mb: int`
- `cpu_percent: float`
- `memory_percent: float`
- `io_ops: float`
- `deadline: float | None`
- `arrival_time: float`
- `priority: int`
- `group: ResourceGroup | None`

### VM profile

Create a dataclass with at least:

- `id: str`
- `cores: int`
- `memory_mb: int`
- `mips_per_core: float`
- `energy_efficiency: float` normalized to 0–1; higher is better
- `utilization: float` normalized to 0–1
- active jobs / queued work state
- performance history

Use a `PerformanceSample` object with:

- completed jobs
- mean runtime
- success rate (0–1)

Provide methods for available CPU, available memory, `can_host(job)`, and normalized historical performance.

Initialize several default VM profiles with distinct CPU/RAM/MIPS/energy trade-offs and initial performance samples.

## Phase 1 — Foundation

Implement the project configuration, core models, default VM profiles, test setup, and a small executable demo.

Acceptance criteria:

- A user can create a `Job` and `VMProfile`.
- A VM correctly reports available resources and job eligibility.
- Each VM has baseline utilization/capacity/performance history.
- `pytest` runs successfully.
- `python -m adaptive_scheduler.main` runs a small simulation/demo.

## Phase 2 — Workload analyzer and adaptive scheduler

### Lightweight classifier

Implement `WorkloadAnalyzer`. It uses the first 10% of a job's execution measurements (represented by the provided `cpu_percent`, `memory_percent`, and `io_ops`) and does not use machine learning or model training.

Suggested deterministic logic:

1. If deadline slack is below a documented threshold, classify as `DEADLINE_CRITICAL`.
2. Normalize I/O appropriately relative to CPU/memory inputs.
3. If resource values are sufficiently close, classify as `BALANCED`.
4. Otherwise use the dominant dimension: CPU, memory, or I/O.

Keep all thresholds in named constants or a configuration dataclass and test every resource group.

### Adaptive VM selection

For every eligible VM, calculate exactly:

```text
Score = 0.4 × Utilization_Match
      + 0.3 × Available_Resources
      + 0.2 × Historical_Performance
      + 0.1 × Energy_Efficiency
```

Requirements:

- Exclude VMs that lack required CPU cores or memory.
- Normalize every score component to 0–1.
- Use a documented target utilization. Deadline-critical jobs should favour lower utilization; ordinary jobs can favour a moderate target.
- Select the highest score.
- Resolve exact score ties by choosing the lower-utilization VM, then a deterministic VM-ID ordering.
- Update VM state after assignment.
- Put weights in `SchedulerWeights` so Phase 3 can change them.

## Phase 3 — Load balancing and feedback

### Load balancer

Continuously check utilization. If:

```text
max_vm_utilization - min_vm_utilization > 0.50
```

attempt to migrate one queued/non-started task from the busiest VM to the least-loaded eligible VM.

Do not migrate a task if it cannot fit on the target. Return a clear migration result object so experiments can count successful and skipped migrations.

### Feedback controller

After each completed job:

- record runtime, SLA success/failure, and energy data;
- update an exponential moving average;
- update VM performance history.

Every 100 completed jobs:

- recalibrate scheduler weights based on the EMA;
- normalize weights so they still sum to 1;
- preserve all four factors, rather than setting any one to zero;
- record the before/after weight values for experiment auditability.

Example policy: if SLA compliance drops below 95%, moderately increase the available-resources weight and reduce utilization-match/historical-performance weights proportionally. Document the policy and make it testable.

## Phase 4 — Baselines, scenarios, and evaluation

### Baseline algorithms

Implement separately and fairly:

1. FCFS: arrival order.
2. Round Robin: cyclic VM assignment.
3. Min-Min: repeatedly select the job with the smallest earliest completion time across VMs.
4. Max-Min: repeatedly select the job with the largest earliest completion time across VMs.
5. Priority: highest priority first; break ties by arrival time.

Do not label a simplified sort-by-length routine as Min-Min or Max-Min. Use estimated completion times and current VM availability.

### Workload scenarios

Implement deterministic workload generators with a supplied seed:

| Scenario | Cloudlets | Distribution |
|---|---:|---|
| Light | 1,000 | Uniform |
| Medium | 2,500 | Exponential |
| Heavy | 5,000 | Bimodal |

Generate realistic, varied resource demands, arrivals, deadlines, and priorities. Ensure identical generated jobs are supplied to every algorithm in the same run.

### Simulation engine

Build a deterministic local discrete-event engine first.

- Simulate per-VM availability and job start/finish timestamps.
- Estimate duration from `length_mi / (allocated_cores × mips_per_core)`.
- Model VM busy time, queueing, utilization, energy, and deadline checks.
- Avoid mutable state leaking between algorithms/runs; deep-copy VM/job templates as required.

Create a `SimulationBackend` protocol/interface and a `CloudSimPlusAdapter` placeholder. The adapter may raise `NotImplementedError` until a Java integration approach is selected.

### Required metrics

Compute all eight metrics:

1. Makespan
2. Response time
3. Waiting time
4. Throughput
5. Resource utilization
6. Load-balancing index
7. Energy consumption
8. SLA violations

Clearly document each formula. For example, define response time and waiting time consistently, and use a documented bounded load-balance index where 1 is ideal.

### Repeated experiments and reporting

- Run each algorithm for every scenario 10 times using distinct, recorded seeds.
- Export raw runs to `outputs/evaluation/simulation_runs.csv`.
- Export grouped statistical results to `outputs/evaluation/statistical_summary.csv`.
- Report mean, sample standard deviation, and 95% confidence interval.
- Compute percent improvement of adaptive scheduling relative to each baseline. For metrics where higher is better, reverse the improvement direction accordingly.

## Phase 5 — Tests, charts, and analysis

Use pytest for unit tests, including at least:

- VM resource calculation and eligibility
- all five classification outcomes
- score calculation / deterministic tie break
- scheduler excludes ineligible VMs
- load-balancer threshold and legal migration
- EMA recalibration at exactly 100 completed jobs
- correctness of all baseline ordering policies
- reproducible workloads for the same seed
- metrics on a tiny known scenario
- no cross-run state contamination

Use Matplotlib and Pandas to save charts under `outputs/evaluation/`:

- makespan by algorithm/scenario
- response time by algorithm/scenario
- utilization / load-balance comparison
- energy consumption comparison
- SLA compliance comparison

Do not claim target improvements as achieved until experiments demonstrate them. Evaluate against these targets:

- 10–20% lower makespan
- 25% faster response time than Min-Min/Max-Min
- 50% better load-balance index
- 95%+ SLA compliance
- 18% energy savings

## Phase 6 — Documentation and paper-ready material

Create `docs/methodology.md` with:

- architecture diagram or concise component description
- scheduler formula and normalized component definitions
- classifier rules and first-10%-measurement assumption
- feedback/recalibration policy
- workload definitions and seeds
- baseline definitions
- metric formulas
- experiment protocol and limitations

Create `docs/contributions.md` with these candidate contributions, phrased cautiously until validated:

1. Training-free lightweight workload classification.
2. Feedback-loop adaptation of transparent scheduler weights.
3. Fair comparison against five standard scheduling baselines under three workload distributions.

Potential future venues: IEEE Transactions on Cloud Computing, Journal of Cloud Computing, and ACM SIGMETRICS. Do not claim acceptance or suitability without a separate literature and scope review.

## Implementation quality rules

- Prefer simple, typed Python dataclasses and pure functions.
- Keep algorithms independent from the simulator backend.
- Use explicit seeds and avoid nondeterministic tests.
- Use meaningful errors rather than silently assigning impossible jobs.
- Avoid global mutable scheduler or VM state.
- Add docstrings where formulas or research assumptions matter.
- Do not add unverified CloudSim Plus Python packages or fake APIs.
- Keep line length around 100 characters and use clear names.

## Exact implementation sequence

Follow these steps in order. At the end of each step, run the stated verification before moving forward. Do not skip ahead to CloudSim Plus integration: the Python system must work independently first.

### Step 1 — Inspect and protect the repository

1. Inspect the existing repository before editing it.
2. Preserve any files that are already present unless they conflict with a clearly identified requirement.
3. Add or update `.gitignore` to exclude `.venv/`, `__pycache__/`, `.pytest_cache/`, `.ruff_cache/`, `.idea/`, build output, and local generated evaluation artifacts.
4. Create the package and test directories listed in the repository structure.
5. Add `src/adaptive_scheduler/__init__.py`.

**Verify:** the directory structure exists and importing the empty package does not fail.

### Step 2 — Configure dependencies and developer commands

1. Add a `pyproject.toml` using Poetry with Python compatibility declared.
2. Add runtime dependencies: NumPy, Pandas, Matplotlib.
3. Add developer dependencies: pytest, pytest-cov, Ruff.
4. Configure pytest to discover tests from `tests/` and import modules from `src/`.
5. Add a README quick-start section with Windows PowerShell commands for creating a virtual environment, installing dependencies, running tests, running a demo, and running the complete evaluation.
6. Add GitHub Actions test workflow for Python 3.11 or a currently supported stable version with package compatibility.

**Verify:** run dependency installation, then `pytest`; an empty/smoke test must execute successfully.

### Step 3 — Implement the domain models (`models.py`)

1. Define `ResourceGroup` as a string enum containing the five exact groups.
2. Define `Job` as a typed dataclass with the fields in the Domain Model section.
3. Define `PerformanceSample` as a typed dataclass.
4. Define `VMProfile` as a typed dataclass.
5. Implement:
   - `available_cores`
   - `available_memory_mb`
   - `can_host(job)`
   - `historical_performance()` returning a bounded 0–1 value
6. Make default values safe: a newly created VM must have a valid utilization and empty active-job/history lists.
7. Do not allow available resources to become negative.

**Tests to add:**

- VM with no active jobs has all resources available.
- VM with one active job reports reduced resources.
- a job needing too many cores is rejected.
- a job needing too much RAM is rejected.
- a VM with no history returns a documented neutral historical-performance score.

**Verify:** run the complete test suite.

### Step 4 — Implement default infrastructure profiles (`engine.py` or `profiles.py`)

1. Create a function such as `default_vm_profiles()` that returns at least four distinct VMs.
2. Give each VM a deliberate hardware profile. Include at least:
   - a high-MIPS VM;
   - an energy-efficient VM;
   - a high-memory VM;
   - a smaller economical VM.
3. Give every VM a non-empty baseline `PerformanceSample` history.
4. Add a concise comment/docstring explaining why its capacity and efficiency values differ.

**Tests to add:**

- every default VM has positive cores, memory, MIPS, and energy efficiency in 0–1;
- all default VM IDs are unique;
- every VM has performance history.

**Verify:** print/read the default profile list in a demo without errors.

### Step 5 — Implement the training-free workload analyzer (`analyzer.py`)

1. Create a `ClassifierConfig` dataclass or named constants for all thresholds.
2. Create `WorkloadAnalyzer.classify(job)`.
3. Evaluate deadline-critical status first using deadline slack. Document the expected time unit and threshold.
4. Normalize or scale I/O input before comparing it to percentages. Never compare a raw large I/O-operation count directly to a percentage.
5. Detect balanced jobs using a configurable tolerance/spread rule.
6. Classify remaining jobs by their dominant normalized demand.
7. Add `analyze(job)` that saves the resulting group on the Job and returns it.

**Tests to add:** exactly one clear test each for CPU-intensive, memory-intensive, I/O-heavy, balanced, and deadline-critical jobs. Also test the deadline rule wins over another dominant resource demand.

**Verify:** all classifier tests pass and thresholds are visible/configurable.

### Step 6 — Implement adaptive scheduling (`scheduler.py`)

1. Create `SchedulerWeights` with initial values 0.4, 0.3, 0.2, 0.1.
2. Add `normalized()` and validate that weights are non-negative and total greater than zero.
3. Create `AdaptiveScheduler` with an analyzer and current weights.
4. Implement the four score components as separate helper methods so each is independently testable:
   - utilization match;
   - available resources;
   - historical performance;
   - energy efficiency.
5. Calculate the weighted total using the exact formula.
6. For each job, run classification before selection.
7. Filter out ineligible VMs before scoring.
8. If no VM is eligible, raise a clear scheduling exception or return a documented unassigned result. Do not silently place the job on an impossible VM.
9. Break equal score ties by lower utilization, then alphabetically/numerically by VM ID for deterministic behaviour.
10. Implement `assign(job, vms)` and update the VM’s queued/active work state only after a successful selection.

**Tests to add:**

- components and total score remain in expected ranges;
- scheduler never selects an ineligible VM;
- tie chooses lower utilization;
- equal utilization tie uses deterministic VM ID;
- a job assignment updates VM state;
- no eligible VM produces the documented error/result.

**Verify:** run a small demo that prints job group, individual eligible VM scores, selected VM, and updated VM state.

### Step 7 — Implement baseline algorithms (`baselines.py`)

1. Define one common return type for all algorithms, ideally ordered `(job, vm)` decisions or a scheduling-plan object.
2. Implement FCFS in arrival-time order.
3. Implement Round Robin by cyclic VM selection. Document how temporarily ineligible choices are handled.
4. Implement Min-Min using a loop: calculate each pending job’s minimum estimated completion time; choose the job whose minimum is smallest; update chosen VM availability; repeat.
5. Implement Max-Min identically, except choose the pending job whose earliest completion time is largest.
6. Implement Priority: descending priority, then earliest arrival time, then job ID.
7. Ensure all algorithms are deterministic.

**Tests to add:**

- FCFS respects arrival ordering;
- Round Robin cycles correctly;
- a controlled tiny matrix proves Min-Min chooses the correct first job;
- a controlled tiny matrix proves Max-Min chooses the correct first job;
- Priority handles ties deterministically.

**Verify:** print planned assignments for five tiny jobs and two VMs.

### Step 8 — Implement workload generation (`workloads.py`)

1. Create `generate_workload(scenario, count=None, seed=...)`.
2. Apply the required default counts: Light 1,000; Medium 2,500; Heavy 5,000.
3. Use:
   - uniform length distribution for Light;
   - exponential length distribution for Medium;
   - clearly documented two-mode mixture for Heavy.
4. Randomize job CPU/memory/I/O demands in valid ranges.
5. Generate arrivals, deadlines, priorities, cores, and memory requirements that are feasible for at least one default VM.
6. Record the seed in every experiment result.
7. Use a local random generator rather than global random state.

**Tests to add:**

- same scenario/count/seed creates identical jobs;
- different seed changes the generated workload;
- each default scenario creates the required count;
- each job can fit on at least one default VM.

**Verify:** run each workload once and print its count plus a compact distribution summary.

### Step 9 — Implement the local discrete-event simulation engine (`engine.py`)

1. Define a clear `Execution`/`JobExecution` result containing job, VM, start, finish, duration, and SLA outcome.
2. Ensure each simulation begins by deep-copying template VMs and jobs. A previous run must not alter the next one.
3. Track available timestamp for every VM.
4. For each assigned job calculate:

   ```text
   start_time = max(arrival_time, vm_available_time)
   execution_time = length_mi / (allocated_cores × vm_mips_per_core)
   finish_time = start_time + execution_time
   ```

5. Update VM availability and busy time.
6. For adaptive scheduling, make scores reflect current simulated VM load at every assignment.
7. For a baseline, execute its generated assignment plan faithfully.
8. Explicitly define whether tasks are non-preemptive. Use non-preemptive scheduling unless a separate feature adds preemption.
9. Add a `ResearchSimulator.run(jobs, algorithm)` public entry point.

**Tests to add:**

- known one-job duration matches the formula;
- two jobs assigned to one VM do not overlap;
- two jobs on separate VMs can overlap;
- repeated runs yield identical outputs;
- a job with a missed deadline is marked as SLA failure.

**Verify:** run a 10–25 job demo with adaptive and every baseline; each returns valid timestamps and metrics.

### Step 10 — Implement load balancing and feedback (`load_balancer.py`, `feedback.py`)

1. Create a `LoadBalancer` with a threshold defaulting to 0.50.
2. Implement a function to identify busiest and least-loaded VMs and return whether the threshold is exceeded.
3. Implement candidate selection for migration from queued/not-yet-started jobs only.
4. Reject migration if the destination cannot host the job.
5. Return a structured result: whether migration happened, source VM, target VM, job ID/reason.
6. Create `FeedbackController` with EMA alpha and recalibration interval 100.
7. After every completion, update SLA success EMA and append/update relevant performance history.
8. At exact multiples of 100 completions, calculate updated weights, normalize them, and persist an audit record.

**Tests to add:**

- difference exactly 0.50 does not migrate (requirement says greater than 50%);
- difference above 0.50 triggers an attempted migration;
- invalid migration is safely skipped;
- EMA is updated after a job;
- recalibration does not happen at 99 jobs and does happen at 100;
- recalibrated weights sum to 1.

**Verify:** use a controlled synthetic VM state to display both a legal migration and a safely rejected migration.

### Step 11 — Implement metrics and experiment reporting (`metrics.py`, `experiments.py`)

1. Define a typed `SimulationMetrics` object with all eight metrics.
2. Implement and document formulas:
   - makespan: maximum finish timestamp;
   - response time: a documented average of start minus arrival, or completion minus arrival—choose one and use it consistently;
   - waiting time: start minus arrival;
   - throughput: completed jobs divided by makespan;
   - resource utilization: aggregate VM busy time divided by available VM-time;
   - load-balancing index: bounded, documented; 1 means ideal;
   - energy: documented energy model using VM busy time and efficiency;
   - SLA violations: count of deadline misses.
3. Implement grouping/reporting utility that produces mean, sample standard deviation, and two-sided 95% confidence interval.
4. Implement percentage-improvement calculation. For lower-is-better metrics, use `(baseline - adaptive) / baseline × 100`; for higher-is-better metrics, use `(adaptive - baseline) / baseline × 100`.
5. Run adaptive plus all five baselines for all three scenarios and all 10 repetitions.
6. Save raw runs and grouped summary CSV files under `outputs/evaluation/`.

**Tests to add:**

- tiny known execution set yields exact makespan, waiting time, and throughput;
- balance index is 1 for equal utilizations;
- mean/std/CI match a known small numeric input;
- percentage-improvement direction is correct for both lower and higher is better.

**Verify:** run a smoke experiment with reduced job counts and two repetitions; inspect CSV headers and row counts before running the full 10-run evaluation.

### Step 12 — Implement charts, documentation, and final validation

1. Add `visualization.py` that reads experiment data or receives a DataFrame and saves PNG charts.
2. Create the five required comparisons: makespan, response time, utilization/load balance, energy consumption, SLA compliance.
3. Include titles, labels, legends, scenario names, and algorithm labels. Use non-interactive Matplotlib output.
4. Write `docs/methodology.md` and `docs/contributions.md` as specified above.
5. Update README with exact commands and a concise architecture/module map.
6. Run linting if configured.
7. Run all tests.
8. Run the demo.
9. Run a smoke evaluation.
10. Run the full prescribed evaluation if runtime permits.
11. Report actual results factually. Do not fabricate target attainment.

**Verify:** confirm tests pass, expected CSV files exist, charts are non-empty, and README commands are accurate.

## Required final response from Gemini

When finished, Gemini must report:

1. Files created/changed, grouped by function.
2. Commands it executed and whether they passed.
3. Test count and test result.
4. Location of CSV outputs and charts.
5. Any known limitations, especially the status of the CloudSim Plus Java integration.
6. Whether a full 10-run experiment was completed; if not, exactly what remains to run.

## Final delivery checklist

Before declaring implementation complete:

1. Run `pytest` and fix failures.
2. Run a small demo.
3. Run at least a smoke evaluation (for example, 2 repetitions and reduced workloads) to verify the entire pipeline.
4. Run the prescribed 10-run evaluation when practical.
5. Verify CSV columns, summary statistics, and chart files exist.
6. Update README with Windows/PyCharm setup, commands, module overview, and how to run experiments.
7. State clearly which CloudSim Plus integration work remains.
