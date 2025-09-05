from Phashcat import flags

def test_core_flags_exist():
    for key in ("HASH_TYPE", "ATTACK_MODE", "OUTFILE", "STATUS"):
        assert hasattr(flags, key), f"missing flags.{key}"

def test_short_to_long_mapping_has_essentials():
    m = flags.SHORT_TO_LONG
    assert m["-m"] == flags.HASH_TYPE
    assert m["-a"] == flags.ATTACK_MODE

def test_value_kind_samples():
    vk = flags.VALUE_KIND
    assert vk[flags.HASH_TYPE] == "Num"
    assert vk[flags.STATUS] is None  # boolean switch

def test_tables_non_empty():
    assert flags.ATTACK_MODES and 3 in flags.ATTACK_MODES
    assert flags.WORKLOAD_PROFILES and 1 in flags.WORKLOAD_PROFILES
