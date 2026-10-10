import pytest
from adaptive_scheduler.models import Job, VMProfile
from adaptive_scheduler.modern_baselines import PSOScheduler, HEFTScheduler, DQNScheduler


@pytest.fixture
def sample_data():
    try:
        j1 = Job("j1", 1000, 50.0, 40.0, 100, 50, 10.0)
        j2 = Job("j2", 5000, 80.0, 70.0, 500, 200, 20.0)
    except TypeError:
        j1 = Job("j1", 1000, 50.0, 40.0, 100, 10.0)
        j2 = Job("j2", 5000, 80.0, 70.0, 500, 20.0)

    try:
        v1 = VMProfile("vm1", 1000, 8, 100, 1.5)
        v2 = VMProfile("vm2", 2500, 16, 200, 2.5)
    except TypeError:
        v1 = VMProfile("vm1", 1000, 8)
        v2 = VMProfile("vm2", 2500, 16)

    return [j1, j2], [v1, v2]


def test_pso_scheduler(sample_data):
    jobs, vms = sample_data
    scheduler = PSOScheduler(num_particles=5, max_iter=10)
    res = scheduler.schedule(jobs, vms)
    assert len(res) == 2


def test_heft_scheduler(sample_data):
    jobs, vms = sample_data
    scheduler = HEFTScheduler()
    res = scheduler.schedule(jobs, vms)
    assert len(res) == 2


def test_dqn_scheduler(sample_data):
    jobs, vms = sample_data
    scheduler = DQNScheduler()
    res = scheduler.schedule(jobs, vms)
    assert len(res) == 2