import random
import numpy as np
from typing import List, Dict, Any
from adaptive_scheduler.models import Job, VMProfile


def _get_job_length(job: Any) -> float:
    for attr in ["length", "instruction_count", "mips_required"]:
        if hasattr(job, attr):
            return float(getattr(job, attr))
    return 1000.0


def _get_vm_mips(vm: Any) -> float:
    for attr in ["mips", "processing_power", "cpu_mips", "capacity", "mips_capacity"]:
        if hasattr(vm, attr):
            return float(getattr(vm, attr))
    return 1000.0


def _get_job_id(job: Any, fallback: str) -> str:
    for attr in ["job_id", "id", "name"]:
        if hasattr(job, attr):
            return str(getattr(job, attr))
    return fallback


def _get_vm_id(vm: Any, fallback: str) -> str:
    for attr in ["vm_id", "id", "name"]:
        if hasattr(vm, attr):
            return str(getattr(vm, attr))
    return fallback


class PSOScheduler:
    """Particle Swarm Optimization baseline for Job-to-VM assignment."""

    def __init__(self, num_particles: int = 15, max_iter: int = 30):
        self.num_particles = num_particles
        self.max_iter = max_iter

    def schedule(self, jobs: List[Job], vms: List[VMProfile]) -> Dict[str, str]:
        if not jobs or not vms:
            return {}

        num_jobs, num_vms = len(jobs), len(vms)
        particles = np.random.randint(0, num_vms, size=(self.num_particles, num_jobs))
        velocities = np.zeros((self.num_particles, num_jobs))

        pbest = particles.copy()
        pbest_scores = np.full(self.num_particles, float("inf"))

        def fitness(position):
            vm_loads = np.zeros(num_vms)
            for j_idx, vm_idx in enumerate(position):
                mips = _get_vm_mips(vms[vm_idx])
                exec_time = _get_job_length(jobs[j_idx]) / (mips if mips > 0 else 1.0)
                vm_loads[vm_idx] += exec_time
            return np.max(vm_loads)

        for i in range(self.num_particles):
            pbest_scores[i] = fitness(particles[i])

        gbest = pbest[np.argmin(pbest_scores)].copy()

        for _ in range(self.max_iter):
            for i in range(self.num_particles):
                r1, r2 = np.random.rand(num_jobs), np.random.rand(num_jobs)
                velocities[i] = 0.5 * velocities[i] + 1.5 * r1 * (pbest[i] - particles[i]) + 1.5 * r2 * (gbest - particles[i])
                particles[i] = np.clip(np.round(particles[i] + velocities[i]), 0, num_vms - 1).astype(int)

                current_fit = fitness(particles[i])
                if current_fit < pbest_scores[i]:
                    pbest_scores[i] = current_fit
                    pbest[i] = particles[i].copy()

            gbest = pbest[np.argmin(pbest_scores)].copy()

        return {_get_job_id(jobs[j], f"j{j}"): _get_vm_id(vms[gbest[j]], f"vm{gbest[j]}") for j in range(num_jobs)}


class HEFTScheduler:
    """Heterogeneous Earliest Finish Time heuristic."""

    def schedule(self, jobs: List[Job], vms: List[VMProfile]) -> Dict[str, str]:
        if not jobs or not vms:
            return {}

        sorted_jobs = sorted(jobs, key=_get_job_length, reverse=True)
        vm_available_times = {_get_vm_id(vm, f"vm{idx}"): 0.0 for idx, vm in enumerate(vms)}
        assignments = {}

        for job in sorted_jobs:
            best_vm = None
            earliest_finish = float("inf")
            j_id = _get_job_id(job, "j")

            for vm in vms:
                v_id = _get_vm_id(vm, "vm")
                mips = _get_vm_mips(vm)
                exec_time = _get_job_length(job) / (mips if mips > 0 else 1.0)
                est_finish = vm_available_times[v_id] + exec_time
                if est_finish < earliest_finish:
                    earliest_finish = est_finish
                    best_vm = vm

            best_v_id = _get_vm_id(best_vm, "vm")
            assignments[j_id] = best_v_id
            vm_available_times[best_v_id] = earliest_finish

        return assignments


class DQNScheduler:
    """Lightweight Q-Learning / Deep-Q baseline proxy."""

    def __init__(self, learning_rate: float = 0.1, discount: float = 0.95):
        self.lr = learning_rate
        self.gamma = discount

    def schedule(self, jobs: List[Job], vms: List[VMProfile]) -> Dict[str, str]:
        if not jobs or not vms:
            return {}

        q_table = np.zeros((5, len(vms)))
        vm_loads = np.zeros(len(vms))
        assignments = {}

        for job in jobs:
            cat = getattr(job, "category", "BALANCED")
            state_idx = hash(cat) % 5
            best_vm_idx = int(np.argmax(q_table[state_idx] - 0.1 * vm_loads))
            
            selected_vm = vms[best_vm_idx]
            mips = _get_vm_mips(selected_vm)
            exec_time = _get_job_length(job) / (mips if mips > 0 else 1.0)
            vm_loads[best_vm_idx] += exec_time

            reward = 100.0 / (exec_time + 1.0)
            q_table[state_idx, best_vm_idx] += self.lr * (reward - q_table[state_idx, best_vm_idx])

            j_id = _get_job_id(job, "j")
            v_id = _get_vm_id(selected_vm, "vm")
            assignments[j_id] = v_id

        return assignments