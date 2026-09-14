from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional


class ResourceGroup(str, Enum):
    CPU_INTENSIVE = "CPU_INTENSIVE"
    MEMORY_INTENSIVE = "MEMORY_INTENSIVE"
    IO_HEAVY = "IO_HEAVY"
    BALANCED = "BALANCED"
    DEADLINE_CRITICAL = "DEADLINE_CRITICAL"


@dataclass
class Job:
    id: str
    length_mi: float
    required_cores: int
    required_memory_mb: int
    cpu_percent: float
    memory_percent: float
    io_ops: float
    deadline: Optional[float] = None
    arrival_time: float = 0.0
    priority: int = 1
    group: Optional[ResourceGroup] = None


@dataclass
class PerformanceSample:
    completed_jobs: int
    mean_runtime: float
    success_rate: float


@dataclass
class VMProfile:
    id: str
    cores: int
    memory_mb: int
    mips_per_core: float
    energy_efficiency: float
    utilization: float = 0.0
    active_jobs: List[Job] = field(default_factory=list)
    queued_work_mi: float = 0.0
    performance_history: List[PerformanceSample] = field(default_factory=list)

    @property
    def available_cores(self) -> int:
        used_cores = sum(job.required_cores for job in self.active_jobs)
        return max(0, self.cores - used_cores)

    @property
    def available_memory_mb(self) -> int:
        used_memory = sum(job.required_memory_mb for job in self.active_jobs)
        return max(0, self.memory_mb - used_memory)

    def can_host(self, job: Job) -> bool:
        return (
            self.available_cores >= job.required_cores
            and self.available_memory_mb >= job.required_memory_mb
        )

    def historical_performance(self) -> float:
        if not self.performance_history:
            return 0.5

        total_jobs = sum(sample.completed_jobs for sample in self.performance_history)
        if total_jobs == 0:
            return 0.5

        weighted_success = sum(
            sample.success_rate * sample.completed_jobs
            for sample in self.performance_history
        )
        return max(0.0, min(1.0, weighted_success / total_jobs))
