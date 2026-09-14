from typing import List
from adaptive_scheduler.models import VMProfile, PerformanceSample


def default_vm_profiles() -> List[VMProfile]:
    """Returns four heterogeneous VM profiles representing distinct hardware trade-offs."""
    return [
        VMProfile(
            id="vm-compute-1",
            cores=8,
            memory_mb=16384,
            mips_per_core=4000.0,
            energy_efficiency=0.70,
            performance_history=[
                PerformanceSample(completed_jobs=50, mean_runtime=3.2, success_rate=0.96)
            ],
        ),
        VMProfile(
            id="vm-eco-1",
            cores=4,
            memory_mb=8192,
            mips_per_core=2500.0,
            energy_efficiency=0.95,
            performance_history=[
                PerformanceSample(completed_jobs=40, mean_runtime=5.1, success_rate=0.98)
            ],
        ),
        VMProfile(
            id="vm-mem-1",
            cores=4,
            memory_mb=32768,
            mips_per_core=2000.0,
            energy_efficiency=0.75,
            performance_history=[
                PerformanceSample(completed_jobs=30, mean_runtime=4.5, success_rate=0.94)
            ],
        ),
        VMProfile(
            id="vm-small-1",
            cores=2,
            memory_mb=4096,
            mips_per_core=1500.0,
            energy_efficiency=0.85,
            performance_history=[
                PerformanceSample(completed_jobs=25, mean_runtime=6.0, success_rate=0.90)
            ],
        ),
    ]