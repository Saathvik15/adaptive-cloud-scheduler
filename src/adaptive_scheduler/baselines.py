from dataclasses import dataclass
from typing import List
from adaptive_scheduler.models import Job, VMProfile


@dataclass
class ScheduleAssignment:
    job: Job
    vm: VMProfile


class BaselineSchedulers:
    @staticmethod
    def _get_execution_time(job: Job, vm: VMProfile) -> float:
        cores = max(1, job.required_cores)
        return job.length_mi / (cores * vm.mips_per_core)

    @classmethod
    def fcfs(cls, jobs: List[Job], vms: List[VMProfile]) -> List[ScheduleAssignment]:
        sorted_jobs = sorted(jobs, key=lambda j: (j.arrival_time, j.id))
        assignments = []
        vm_ready_times = {vm.id: 0.0 for vm in vms}

        for job in sorted_jobs:
            eligible = [vm for vm in vms if vm.can_host(job)]
            if not eligible:
                continue
            best_vm = min(eligible, key=lambda vm: (vm_ready_times[vm.id], vm.id))
            exec_time = cls._get_execution_time(job, best_vm)
            start_time = max(job.arrival_time, vm_ready_times[best_vm.id])
            vm_ready_times[best_vm.id] = start_time + exec_time
            assignments.append(ScheduleAssignment(job=job, vm=best_vm))

        return assignments

    @classmethod
    def round_robin(cls, jobs: List[Job], vms: List[VMProfile]) -> List[ScheduleAssignment]:
        sorted_jobs = sorted(jobs, key=lambda j: (j.arrival_time, j.id))
        assignments = []
        vm_idx = 0
        num_vms = len(vms)

        for job in sorted_jobs:
            attempts = 0
            while attempts < num_vms:
                candidate_vm = vms[vm_idx % num_vms]
                vm_idx = (vm_idx + 1) % num_vms
                attempts += 1
                if candidate_vm.can_host(job):
                    assignments.append(ScheduleAssignment(job=job, vm=candidate_vm))
                    break

        return assignments

    @classmethod
    def min_min(cls, jobs: List[Job], vms: List[VMProfile]) -> List[ScheduleAssignment]:
        remaining_jobs = list(jobs)
        vm_ready_times = {vm.id: 0.0 for vm in vms}
        assignments = []

        while remaining_jobs:
            job_min_completion = []
            for job in remaining_jobs:
                eligible = [vm for vm in vms if vm.can_host(job)]
                if not eligible:
                    continue
                best_vm_for_job = None
                earliest_completion = float("inf")
                for vm in eligible:
                    exec_time = cls._get_execution_time(job, vm)
                    start_time = max(job.arrival_time, vm_ready_times[vm.id])
                    completion = start_time + exec_time
                    if completion < earliest_completion:
                        earliest_completion = completion
                        best_vm_for_job = vm
                if best_vm_for_job:
                    job_min_completion.append((earliest_completion, job, best_vm_for_job))

            if not job_min_completion:
                break

            # Min-Min: select job with overall SMALLEST earliest completion time
            job_min_completion.sort(key=lambda x: (x[0], x[1].id))
            _, chosen_job, chosen_vm = job_min_completion[0]

            exec_time = cls._get_execution_time(chosen_job, chosen_vm)
            start_time = max(chosen_job.arrival_time, vm_ready_times[chosen_vm.id])
            vm_ready_times[chosen_vm.id] = start_time + exec_time

            assignments.append(ScheduleAssignment(job=chosen_job, vm=chosen_vm))
            remaining_jobs.remove(chosen_job)

        return assignments

    @classmethod
    def max_min(cls, jobs: List[Job], vms: List[VMProfile]) -> List[ScheduleAssignment]:
        remaining_jobs = list(jobs)
        vm_ready_times = {vm.id: 0.0 for vm in vms}
        assignments = []

        while remaining_jobs:
            job_min_completion = []
            for job in remaining_jobs:
                eligible = [vm for vm in vms if vm.can_host(job)]
                if not eligible:
                    continue
                best_vm_for_job = None
                earliest_completion = float("inf")
                for vm in eligible:
                    exec_time = cls._get_execution_time(job, vm)
                    start_time = max(job.arrival_time, vm_ready_times[vm.id])
                    completion = start_time + exec_time
                    if completion < earliest_completion:
                        earliest_completion = completion
                        best_vm_for_job = vm
                if best_vm_for_job:
                    job_min_completion.append((earliest_completion, job, best_vm_for_job))

            if not job_min_completion:
                break

            # Max-Min: select job with overall LARGEST earliest completion time
            job_min_completion.sort(key=lambda x: (-x[0], x[1].id))
            _, chosen_job, chosen_vm = job_min_completion[0]

            exec_time = cls._get_execution_time(chosen_job, chosen_vm)
            start_time = max(chosen_job.arrival_time, vm_ready_times[chosen_vm.id])
            vm_ready_times[chosen_vm.id] = start_time + exec_time

            assignments.append(ScheduleAssignment(job=chosen_job, vm=chosen_vm))
            remaining_jobs.remove(chosen_job)

        return assignments

    @classmethod
    def priority(cls, jobs: List[Job], vms: List[VMProfile]) -> List[ScheduleAssignment]:
        # Priority descending (higher int = higher priority), then arrival time
        sorted_jobs = sorted(jobs, key=lambda j: (-j.priority, j.arrival_time, j.id))
        assignments = []
        vm_ready_times = {vm.id: 0.0 for vm in vms}

        for job in sorted_jobs:
            eligible = [vm for vm in vms if vm.can_host(job)]
            if not eligible:
                continue
            best_vm = min(eligible, key=lambda vm: (vm_ready_times[vm.id], vm.id))
            exec_time = cls._get_execution_time(job, best_vm)
            start_time = max(job.arrival_time, vm_ready_times[best_vm.id])
            vm_ready_times[best_vm.id] = start_time + exec_time
            assignments.append(ScheduleAssignment(job=job, vm=best_vm))

        return assignments