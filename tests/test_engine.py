import pytest
from adaptive_scheduler.engine import SimulationEngine
from adaptive_scheduler.profiles import default_vm_profiles
from adaptive_scheduler.scheduler import AdaptiveScheduler
from adaptive_scheduler.workloads import generate_workload


@pytest.fixture
def vms():
    return default_vm_profiles()


@pytest.fixture
def small_workload():
    return generate_workload("light", count=20, seed=42)


def test_simulation_engine_adaptive(vms, small_workload):
    engine = SimulationEngine(vms)
    scheduler = AdaptiveScheduler()
    metrics = engine.run_adaptive(small_workload, scheduler)

    assert metrics.total_jobs == 20
    assert metrics.completed_jobs == 20
    assert metrics.makespan > 0.0
    assert metrics.avg_turnaround_time > 0.0
    assert 0.0 <= metrics.deadline_miss_rate <= 1.0
    assert metrics.energy_consumed_kwh > 0.0


def test_simulation_engine_baseline(vms, small_workload):
    engine = SimulationEngine(vms)
    metrics = engine.run_baseline(small_workload, "fcfs")

    assert metrics.total_jobs == 20
    assert metrics.completed_jobs == 20
    assert metrics.makespan > 0.0


def test_invalid_baseline_algorithm(vms, small_workload):
    engine = SimulationEngine(vms)
    with pytest.raises(ValueError):
        engine.run_baseline(small_workload, "invalid_algo")