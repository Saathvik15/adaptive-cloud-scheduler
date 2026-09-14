from dataclasses import dataclass
from typing import List, Tuple
from adaptive_scheduler.analyzer import WorkloadAnalyzer
from adaptive_scheduler.models import Job, ResourceGroup, VMProfile


class NoEligibleVMError(Exception):
    """Raised when no VM can host the requested job."""
    pass


@dataclass
class SchedulerWeights:
    utilization_match: float = 0.4
    available_resources: float = 0.3
    historical_performance: float = 0.2
    energy_efficiency: float = 0.1

    def normalized(self) -> "SchedulerWeights":
        total = (
            self.utilization_match
            + self.available_resources
            + self.historical_performance
            + self.energy_efficiency
        )
        if total <= 0:
            raise ValueError("Sum of scheduler weights must be positive.")
        return SchedulerWeights(
            utilization_match=self.utilization_match / total,
            available_resources=self.available_resources / total,
            historical_performance=self.historical_performance / total,
            energy_efficiency=self.energy_efficiency / total,
        )


class AdaptiveScheduler:
    def __init__(
        self,
        analyzer: WorkloadAnalyzer | None = None,
        weights: SchedulerWeights | None = None,
    ):
        self.analyzer = analyzer or WorkloadAnalyzer()
        self.weights = (weights or SchedulerWeights()).normalized()

    def calculate_utilization_match(self, vm: VMProfile, job: Job) -> float:
        # Favor lower utilization for urgent/deadline jobs; moderate utilization for standard jobs
        target = 0.4 if job.group == ResourceGroup.DEADLINE_CRITICAL else 0.7
        match_score = 1.0 - abs(target - vm.utilization)
        return max(0.0, min(1.0, match_score))

    def calculate_available_resources(self, vm: VMProfile) -> float:
        core_ratio = vm.available_cores / vm.cores if vm.cores > 0 else 0.0
        mem_ratio = vm.available_memory_mb / vm.memory_mb if vm.memory_mb > 0 else 0.0
        return (core_ratio + mem_ratio) / 2.0

    def calculate_score(self, vm: VMProfile, job: Job) -> float:
        s_util = self.calculate_utilization_match(vm, job)
        s_res = self.calculate_available_resources(vm)
        s_hist = vm.historical_performance()
        s_eng = vm.energy_efficiency

        w = self.weights
        total = (
            w.utilization_match * s_util
            + w.available_resources * s_res
            + w.historical_performance * s_hist
            + w.energy_efficiency * s_eng
        )
        return max(0.0, min(1.0, total))

    def select_vm(self, job: Job, vms: List[VMProfile]) -> Tuple[VMProfile, float]:
        # 1. Run workload analysis/classification first
        if job.group is None:
            self.analyzer.analyze(job)

        # 2. Filter out VMs that lack capacity
        eligible = [vm for vm in vms if vm.can_host(job)]
        if not eligible:
            raise NoEligibleVMError(f"No VM has sufficient resources to host Job {job.id}")

        # 3. Score eligible VMs and break ties (highest score, lower utilization, VM ID)
        scored_vms = []
        for vm in eligible:
            score = self.calculate_score(vm, job)
            scored_vms.append((score, vm.utilization, vm.id, vm))

        # Sort: descending score, ascending utilization, ascending VM ID
        scored_vms.sort(key=lambda item: (-item[0], item[1], item[2]))
        
        best_tuple = scored_vms[0]
        return best_tuple[3], best_tuple[0]

    def assign(self, job: Job, vms: List[VMProfile]) -> Tuple[VMProfile, float]:
        best_vm, score = self.select_vm(job, vms)
        best_vm.active_jobs.append(job)
        best_vm.queued_work_mi += job.length_mi
        return best_vm, score