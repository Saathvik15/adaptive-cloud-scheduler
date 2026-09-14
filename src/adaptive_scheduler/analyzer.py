from dataclasses import dataclass
from adaptive_scheduler.models import Job, ResourceGroup


@dataclass
class ClassifierConfig:
    deadline_slack_threshold: float = 10.0  # Slack below this is deadline-critical
    io_scale_factor: float = 10.0  # Scales raw io_ops into a 0-100 percentage range
    balanced_tolerance: float = 15.0  # Max spread between normalized metrics for BALANCED


class WorkloadAnalyzer:
    def __init__(self, config: ClassifierConfig = ClassifierConfig()):
        self.config = config

    def classify(self, job: Job) -> ResourceGroup:
        # 1. Deadline urgency check (wins over resource dominance)
        if job.deadline is not None:
            slack = job.deadline - job.arrival_time
            if slack <= self.config.deadline_slack_threshold:
                return ResourceGroup.DEADLINE_CRITICAL

        # 2. Normalize I/O to a 0-100% scale comparable with CPU/RAM percentages
        norm_io = min(100.0, job.io_ops / self.config.io_scale_factor)

        metrics = {
            ResourceGroup.CPU_INTENSIVE: job.cpu_percent,
            ResourceGroup.MEMORY_INTENSIVE: job.memory_percent,
            ResourceGroup.IO_HEAVY: norm_io,
        }

        vals = list(metrics.values())

        # 3. Check if demand spread is close enough to be considered BALANCED
        if (max(vals) - min(vals)) <= self.config.balanced_tolerance:
            return ResourceGroup.BALANCED

        # 4. Classify by dominant resource usage
        return max(metrics, key=metrics.get)

    def analyze(self, job: Job) -> ResourceGroup:
        group = self.classify(job)
        job.group = group
        return group