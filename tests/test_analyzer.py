import pytest
from adaptive_scheduler.analyzer import ClassifierConfig, WorkloadAnalyzer
from adaptive_scheduler.models import Job, ResourceGroup


@pytest.fixture
def analyzer():
    return WorkloadAnalyzer(
        ClassifierConfig(deadline_slack_threshold=10.0, io_scale_factor=10.0)
    )


def test_classify_deadline_critical(analyzer):
    job = Job(
        "j1",
        1000.0,
        2,
        2048,
        cpu_percent=90.0,
        memory_percent=10.0,
        io_ops=5.0,
        arrival_time=0.0,
        deadline=5.0,
    )
    assert analyzer.classify(job) == ResourceGroup.DEADLINE_CRITICAL


def test_classify_cpu_intensive(analyzer):
    job = Job("j2", 1000.0, 2, 2048, cpu_percent=85.0, memory_percent=20.0, io_ops=10.0)
    assert analyzer.classify(job) == ResourceGroup.CPU_INTENSIVE


def test_classify_memory_intensive(analyzer):
    job = Job("j3", 1000.0, 2, 2048, cpu_percent=20.0, memory_percent=85.0, io_ops=10.0)
    assert analyzer.classify(job) == ResourceGroup.MEMORY_INTENSIVE


def test_classify_io_heavy(analyzer):
    job = Job("j4", 1000.0, 2, 2048, cpu_percent=20.0, memory_percent=10.0, io_ops=850.0)
    assert analyzer.classify(job) == ResourceGroup.IO_HEAVY


def test_classify_balanced(analyzer):
    job = Job("j5", 1000.0, 2, 2048, cpu_percent=45.0, memory_percent=40.0, io_ops=420.0)
    assert analyzer.classify(job) == ResourceGroup.BALANCED


def test_analyze_sets_job_group(analyzer):
    job = Job("j6", 1000.0, 2, 2048, cpu_percent=90.0, memory_percent=10.0, io_ops=5.0)
    group = analyzer.analyze(job)
    assert group == ResourceGroup.CPU_INTENSIVE
    assert job.group == ResourceGroup.CPU_INTENSIVE