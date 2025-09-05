from Phashcat import hashcat, HashcatBuilder, flags

def test_fluent_chain_value_order_and_positionals():
    cmd = (
        hashcat("hashes.txt", "?d?d?d?d?d?d")
        .hash_type(0)
        .attack_mode(3)
        .outfile("cracked.txt")
        .status(True)
        .value()
    )
    # binary + sorted flags + positionals
    assert isinstance(cmd, list) and len(cmd) >= 2
    assert cmd[0].endswith("hashcat") or "hashcat" in cmd[0]
    # flags must appear before positionals
    assert "hashes.txt" in cmd and "?d?d?d?d?d?d" in cmd
    pos_idx = cmd.index("hashes.txt")
    # ensure at least one flag appears before positionals
    assert flags.ATTACK_MODE in cmd[:pos_idx]
    assert flags.HASH_TYPE in cmd[:pos_idx]
    assert flags.OUTFILE in cmd[:pos_idx]
    assert flags.STATUS in cmd[:pos_idx]

def test_immutability():
    base = hashcat("h.txt").hash_type(0)
    v1 = base.attack_mode(3)
    v2 = base.attack_mode(0)
    assert v1 is not base and v2 is not base and v1 is not v2
    assert flags.ATTACK_MODE in v1._opts and v1._opts[flags.ATTACK_MODE] == 3
    assert flags.ATTACK_MODE in v2._opts and v2._opts[flags.ATTACK_MODE] == 0
    # base unchanged
    assert flags.ATTACK_MODE not in base._opts

def test_set_unset_and_arg_order():
    b = hashcat().set(flags.STATUS, True).unset(flags.STATUS)
    assert flags.STATUS not in b._opts
    b = b.arg("a.hash").arg("dict.txt")
    assert b._positionals == ["a.hash", "dict.txt"]

def test_cmdline_quotes_no_crash():
    line = (
        hashcat("weird file.hash", "my dict.txt")
        .hash_type(0).attack_mode(0).outfile("out file.txt")
        .cmdline()
    )
    assert isinstance(line, str) and "out file.txt" in line
