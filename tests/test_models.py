import pytest
from adaptive_scheduler.models import Job, PerformanceSample, VMProfile


def test_vm_full_resources_when_idle():
    vm = VMProfile(id="vm-1", cores=4, memory_mb=8192, mips_per_core=2500.0, energy_efficiency=0.85)
    assert vm.available_cores == 4
    assert vm.available_memory_mb == 8192


def test_vm_reduced_resources_with_active_job():
    vm = VMProfile(id="vm-1", cores=4, memory_mb=8192, mips_per_core=2500.0, energy_efficiency=0.85)
    job = Job("j-1", 1000.0, 2, 2048, 50.0, 30.0, 10.0)
    vm.active_jobs.append(job)

    assert vm.available_cores == 2
    assert vm.available_memory_mb == 6144


def test_can_host_rejects_exceeding_cores():
    vm = VMProfile(id="vm-1", cores=2, memory_mb=8192, mips_per_core=2500.0, energy_efficiency=0.85)
    job = Job("j-1", 1000.0, 4, 2048, 50.0, 30.0, 10.0)
    assert vm.can_host(job) is False


def test_historical_performance_neutral_baseline():
    vm = VMProfile(id="vm-1", cores=4, memory_mb=8192, mips_per_core=2500.0, energy_efficiency=0.85)
    assert vm.historical_performance() == 0.5


def test_historical_performance_weighted_average():
    vm = VMProfile(id="vm-1", cores=4, memory_mb=8192, mips_per_core=2500.0, energy_efficiency=0.85)
    vm.performance_history.append(PerformanceSample(10, 5.0, 0.9))
    vm.performance_history.append(PerformanceSample(10, 4.0, 1.0))
    assert vm.historical_performance() == pytest.approx(0.95)
