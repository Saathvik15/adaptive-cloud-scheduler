import pytest
from adaptive_scheduler.models import Job, VMProfile
from adaptive_scheduler.scheduler import (
    AdaptiveScheduler,
    NoEligibleVMError,
    SchedulerWeights,
)


def test_weights_normalization():
    w = SchedulerWeights(0.8, 0.6, 0.4, 0.2).normalized()
    assert pytest.approx(w.utilization_match) == 0.4
    assert pytest.approx(w.available_resources) == 0.3
    assert pytest.approx(w.historical_performance) == 0.2
    assert pytest.approx(w.energy_efficiency) == 0.1


def test_scheduler_excludes_ineligible_vm():
    scheduler = AdaptiveScheduler()
    small_vm = VMProfile(
        "vm-small",
        cores=1,
        memory_mb=1024,
        mips_per_core=1000.0,
        energy_efficiency=0.9,
    )
    large_job = Job(
        "j1",
        1000.0,
        required_cores=4,
        required_memory_mb=4096,
        cpu_percent=50.0,
        memory_percent=50.0,
        io_ops=10.0,
    )

    with pytest.raises(NoEligibleVMError):
        scheduler.select_vm(large_job, [small_vm])


def test_scheduler_tie_breaking():
    scheduler = AdaptiveScheduler()
    job = Job(
        "j1",
        1000.0,
        required_cores=2,
        required_memory_mb=2048,
        cpu_percent=50.0,
        memory_percent=50.0,
        io_ops=10.0,
    )

    # Both utilizations are distance 0.2 from target 0.7, yielding identical scores (0.8)
    vm1 = VMProfile(
        "vm-1",
        cores=4,
        memory_mb=8192,
        mips_per_core=2000.0,
        energy_efficiency=0.8,
        utilization=0.9,
    )
    vm2 = VMProfile(
        "vm-2",
        cores=4,
        memory_mb=8192,
        mips_per_core=2000.0,
        energy_efficiency=0.8,
        utilization=0.5,
    )

    selected_vm, _ = scheduler.select_vm(job, [vm1, vm2])
    assert selected_vm.id == "vm-2"


def test_assign_updates_vm_state():
    scheduler = AdaptiveScheduler()
    vm = VMProfile(
        "vm-1",
        cores=4,
        memory_mb=8192,
        mips_per_core=2000.0,
        energy_efficiency=0.8,
    )
    job = Job(
        "j1",
        1000.0,
        required_cores=2,
        required_memory_mb=2048,
        cpu_percent=50.0,
        memory_percent=50.0,
        io_ops=10.0,
    )

    assigned_vm, score = scheduler.assign(job, [vm])
    assert assigned_vm.id == "vm-1"
    assert len(vm.active_jobs) == 1
    assert vm.queued_work_mi == 1000.0
    assert 0.0 <= score <= 1.0