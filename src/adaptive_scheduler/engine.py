from dataclasses import dataclass
from typing import List
from adaptive_scheduler.baselines import BaselineSchedulers
from adaptive_scheduler.models import Job, VMProfile
from adaptive_scheduler.scheduler import AdaptiveScheduler


@dataclass
class SimulationMetrics:
    makespan: float
    avg_turnaround_time: float
    avg_waiting_time: float
    deadline_miss_rate: float
    energy_consumed_kwh: float
    total_jobs: int
    completed_jobs: int


class SimulationEngine:
    def __init__(self, vms: List[VMProfile]):
        # Create fresh VM instances to isolate state between runs
        self.vms = [
            VMProfile(
                id=vm.id,
                cores=vm.cores,
                memory_mb=vm.memory_mb,
                mips_per_core=vm.mips_per_core,
                energy_efficiency=vm.energy_efficiency,
                utilization=vm.utilization,
            )
            for vm in vms
        ]

    def run_adaptive(self, jobs: List[Job], scheduler: AdaptiveScheduler) -> SimulationMetrics:
        sorted_jobs = sorted(jobs, key=lambda j: (j.arrival_time, j.id))
        vm_ready_times = {vm.id: 0.0 for vm in self.vms}

        turnaround_times = []
        waiting_times = []
        deadline_misses = 0
        total_energy = 0.0

        for job in sorted_jobs:
            best_vm, _ = scheduler.select_vm(job, self.vms)

            cores = max(1, job.required_cores)
            exec_time = job.length_mi / (cores * best_vm.mips_per_core)

            start_time = max(job.arrival_time, vm_ready_times[best_vm.id])
            finish_time = start_time + exec_time
            vm_ready_times[best_vm.id] = finish_time

            wait_time = start_time - job.arrival_time
            turnaround = finish_time - job.arrival_time

            waiting_times.append(wait_time)
            turnaround_times.append(turnaround)

            if job.deadline is not None and finish_time > job.deadline:
                deadline_misses += 1

            power_kw = (cores * 0.1) * (1.1 - best_vm.energy_efficiency)
            total_energy += power_kw * (exec_time / 3600.0)

        makespan = max(vm_ready_times.values()) if vm_ready_times else 0.0
        total_jobs = len(jobs)

        return SimulationMetrics(
            makespan=makespan,
            avg_turnaround_time=sum(turnaround_times) / total_jobs if total_jobs > 0 else 0.0,
            avg_waiting_time=sum(waiting_times) / total_jobs if total_jobs > 0 else 0.0,
            deadline_miss_rate=deadline_misses / total_jobs if total_jobs > 0 else 0.0,
            energy_consumed_kwh=total_energy,
            total_jobs=total_jobs,
            completed_jobs=total_jobs,
        )

    def run_baseline(self, jobs: List[Job], algorithm_name: str) -> SimulationMetrics:
        algo_map = {
            "fcfs": BaselineSchedulers.fcfs,
            "round_robin": BaselineSchedulers.round_robin,
            "min_min": BaselineSchedulers.min_min,
            "max_min": BaselineSchedulers.max_min,
            "priority": BaselineSchedulers.priority,
        }

        algo_lower = algorithm_name.lower()
        if algo_lower not in algo_map:
            raise ValueError(f"Unknown baseline algorithm: '{algorithm_name}'. Choose from: {list(algo_map.keys())}")

        assignments = algo_map[algo_lower](jobs, self.vms)
        vm_ready_times = {vm.id: 0.0 for vm in self.vms}

        turnaround_times = []
        waiting_times = []
        deadline_misses = 0
        total_energy = 0.0

        for assign in assignments:
            job = assign.job
            vm = assign.vm

            cores = max(1, job.required_cores)
            exec_time = job.length_mi / (cores * vm.mips_per_core)

            start_time = max(job.arrival_time, vm_ready_times[vm.id])
            finish_time = start_time + exec_time
            vm_ready_times[vm.id] = finish_time

            wait_time = start_time - job.arrival_time
            turnaround = finish_time - job.arrival_time

            waiting_times.append(wait_time)
            turnaround_times.append(turnaround)

            if job.deadline is not None and finish_time > job.deadline:
                deadline_misses += 1

            power_kw = (cores * 0.1) * (1.1 - vm.energy_efficiency)
            total_energy += power_kw * (exec_time / 3600.0)

        makespan = max(vm_ready_times.values()) if vm_ready_times else 0.0
        total_jobs = len(jobs)

        return SimulationMetrics(
            makespan=makespan,
            avg_turnaround_time=sum(turnaround_times) / total_jobs if total_jobs > 0 else 0.0,
            avg_waiting_time=sum(waiting_times) / total_jobs if total_jobs > 0 else 0.0,
            deadline_miss_rate=deadline_misses / total_jobs if total_jobs > 0 else 0.0,
            energy_consumed_kwh=total_energy,
            total_jobs=total_jobs,
            completed_jobs=len(assignments),
        )