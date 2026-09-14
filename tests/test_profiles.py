from adaptive_scheduler.profiles import default_vm_profiles


def test_default_vm_profiles_properties():
    profiles = default_vm_profiles()
    assert len(profiles) >= 4

    ids = set()
    for vm in profiles:
        assert vm.cores > 0
        assert vm.memory_mb > 0
        assert vm.mips_per_core > 0.0
        assert 0.0 <= vm.energy_efficiency <= 1.0
        assert len(vm.performance_history) > 0
        assert vm.id not in ids
        ids.add(vm.id)