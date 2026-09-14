import pytest
from adaptive_scheduler.baselines import BaselineSchedulers
from adaptive_scheduler.models import Job, VMProfile


@pytest.fixture
def sample_vms():
    return [
        VMProfile("vm-1", cores=4, memory_mb=8192, mips_per_core=2000.0, energy_efficiency=0.8),
        VMProfile("vm-2", cores=4, memory_mb=8192, mips_per_core=1000.0, energy_efficiency=0.8),
    ]


def test_fcfs_respects_arrival_order(sample_vms):
    j1 = Job("j1", 1000.0, 2, 2048, 50.0, 50.0, 10.0, arrival_time=2.0)
    j2 = Job("j2", 1000.0, 2, 2048, 50.0, 50.0, 10.0, arrival_time=1.0)

    assignments = BaselineSchedulers.fcfs([j1, j2], sample_vms)
    assert [a.job.id for a in assignments] == ["j2", "j1"]


def test_round_robin_cycles_vms(sample_vms):
    j1 = Job("j1", 1000.0, 2, 2048, 50.0, 50.0, 10.0)
    j2 = Job("j2", 1000.0, 2, 2048, 50.0, 50.0, 10.0)

    assignments = BaselineSchedulers.round_robin([j1, j2], sample_vms)
    assert assignments[0].vm.id == "vm-1"
    assert assignments[1].vm.id == "vm-2"


def test_min_min_schedules_shortest_completion_first(sample_vms):
    # Short job (100 MI) vs Long job (10,000 MI)
    j_short = Job("j-short", 100.0, 2, 2048, 50.0, 50.0, 10.0)
    j_long = Job("j-long", 10000.0, 2, 2048, 50.0, 50.0, 10.0)

    assignments = BaselineSchedulers.min_min([j_long, j_short], sample_vms)
    assert assignments[0].job.id == "j-short"


def test_max_min_schedules_longest_completion_first(sample_vms):
    j_short = Job("j-short", 100.0, 2, 2048, 50.0, 50.0, 10.0)
    j_long = Job("j-long", 10000.0, 2, 2048, 50.0, 50.0, 10.0)

    assignments = BaselineSchedulers.max_min([j_short, j_long], sample_vms)
    assert assignments[0].job.id == "j-long"


def test_priority_ordering(sample_vms):
    j_low = Job("j-low", 1000.0, 2, 2048, 50.0, 50.0, 10.0, priority=1)
    j_high = Job("j-high", 1000.0, 2, 2048, 50.0, 50.0, 10.0, priority=5)

    assignments = BaselineSchedulers.priority([j_low, j_high], sample_vms)
    assert assignments[0].job.id == "j-high"