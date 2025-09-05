from Phashcat import hashcat, HashcatBuilder

def test_identity_law():
    e = HashcatBuilder.empty()
    a = hashcat("h.hash").hash_type(0)
    assert a.mappend(e).cmdline() == a.cmdline()
    assert e.mappend(a).cmdline() == a.cmdline()

def test_associativity():
    a = hashcat().hash_type(0)
    b = hashcat().attack_mode(3)
    c = hashcat().outfile("o.txt")
    left = a.mappend(b).mappend(c)
    right = a.mappend(b.mappend(c))
    assert left.cmdline() == right.cmdline()

def test_right_bias_override_and_positional_concat():
    a = hashcat("h1").hash_type(0)
    b = hashcat("h2").hash_type(1000)  # override hash type
    m = a.mappend(b)
    # right bias on option:
    assert m._opts.get("--hash-type") == 1000
    # positionals concatenated:
    assert m._positionals == ["h1", "h2"]
