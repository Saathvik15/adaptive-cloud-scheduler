import pytest
from adaptive_scheduler.profiles import default_vm_profiles
from adaptive_scheduler.workloads import generate_workload


def test_workload_reproducibility():
    jobs_a = generate_workload("light", count=50, seed=123)
    jobs_b = generate_workload("light", count=50, seed=123)

    assert len(jobs_a) == len(jobs_b) == 50
    for ja, jb in zip(jobs_a, jobs_b):
        assert ja.id == jb.id
        assert ja.length_mi == pytest.approx(jb.length_mi)
        assert ja.arrival_time == pytest.approx(jb.arrival_time)


def test_seed_changes_generated_workload():
    jobs_a = generate_workload("light", count=50, seed=123)
    jobs_b = generate_workload("light", count=50, seed=456)

    assert jobs_a[0].length_mi != jobs_b[0].length_mi


def test_default_scenario_counts():
    assert len(generate_workload("light", seed=42)) == 1000
    assert len(generate_workload("medium", seed=42)) == 2500
    assert len(generate_workload("heavy", seed=42)) == 5000


def test_all_jobs_fit_on_at_least_one_default_vm():
    vms = default_vm_profiles()
    jobs = generate_workload("heavy", count=200, seed=42)

    for job in jobs:
        can_fit = any(vm.can_host(job) for vm in vms)
        assert can_fit, f"Job {job.id} requires {job.required_cores} cores / {job.required_memory_mb}MB RAM and fits no VM."