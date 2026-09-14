from typing import List, Optional
import numpy as np
from adaptive_scheduler.models import Job


SCENARIO_DEFAULTS = {
    "light": 1000,
    "medium": 2500,
    "heavy": 5000,
}


def generate_workload(
    scenario: str,
    count: Optional[int] = None,
    seed: int = 42,
) -> List[Job]:
    """Generates synthetic cloud workloads for Light, Medium, or Heavy scenarios.

    Uses an isolated RNG instance for strict reproducibility.
    """
    scenario_lower = scenario.lower()
    if scenario_lower not in SCENARIO_DEFAULTS:
        raise ValueError(
            f"Unknown scenario '{scenario}'. Choose from: {list(SCENARIO_DEFAULTS.keys())}"
        )

    num_jobs = count if count is not None else SCENARIO_DEFAULTS[scenario_lower]
    rng = np.random.default_rng(seed)

    # 1. Job length (MI) distributions based on scenario
    if scenario_lower == "light":
        lengths = rng.uniform(500.0, 5000.0, size=num_jobs)
    elif scenario_lower == "medium":
        lengths = rng.exponential(scale=2500.0, size=num_jobs) + 200.0
    else:  # Heavy: Bimodal mixture model (50% small jobs, 50% intensive jobs)
        modes = rng.choice([0, 1], size=num_jobs)
        mode_0 = rng.normal(loc=1500.0, scale=300.0, size=num_jobs)
        mode_1 = rng.normal(loc=12000.0, scale=2000.0, size=num_jobs)
        lengths = np.where(modes == 0, mode_0, mode_1)

    lengths = np.clip(lengths, 100.0, 50000.0)

    # 2. Resource demands (feasible for default hardware profiles)
    cores_options = np.array([1, 2, 4])
    cores = rng.choice(cores_options, size=num_jobs)

    mem_options = np.array([1024, 2048, 4096, 8192])
    memories = rng.choice(mem_options, size=num_jobs)

    cpu_percents = rng.uniform(10.0, 95.0, size=num_jobs)
    mem_percents = rng.uniform(10.0, 95.0, size=num_jobs)
    io_ops = rng.uniform(1.0, 1000.0, size=num_jobs)

    # 3. Time attributes: arrival times and deadline slacks
    arrival_intervals = rng.exponential(scale=2.0, size=num_jobs)
    arrival_times = np.cumsum(arrival_intervals) - arrival_intervals[0]

    slacks = rng.uniform(5.0, 60.0, size=num_jobs)
    deadlines = arrival_times + (lengths / 1000.0) + slacks

    priorities = rng.integers(1, 6, size=num_jobs)  # Priority scale 1-5

    jobs = []
    for i in range(num_jobs):
        jobs.append(
            Job(
                id=f"job-{scenario_lower}-{i+1}",
                length_mi=float(lengths[i]),
                required_cores=int(cores[i]),
                required_memory_mb=int(memories[i]),
                cpu_percent=float(cpu_percents[i]),
                memory_percent=float(mem_percents[i]),
                io_ops=float(io_ops[i]),
                deadline=float(deadlines[i]),
                arrival_time=float(arrival_times[i]),
                priority=int(priorities[i]),
            )
        )

    return jobs