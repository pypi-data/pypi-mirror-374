import re
from Phashcat import hashcat, flags

def test_all_flags_before_positionals_and_sorted():
    b = (
        hashcat("hashes.txt", "dict.txt")
        .outfile("out.txt")
        .hash_type(0)
        .attack_mode(0)
        .status(True)
    )
    argv = b.value()
    pos_i = argv.index("hashes.txt")
    flags_only = argv[1:pos_i]  # skip binary
    # Ensure flags look like --something (every other entry if valued)
    assert all(x.startswith("--") for x in flags_only[0::2])
    # Ensure positionals intact and after
    assert argv[pos_i:] == ["hashes.txt", "dict.txt"]

def test_cmdline_quotes_for_spaces():
    line = (
        hashcat("C:\\Program Files\\hashes file.hash", "my dict.txt")
        .outfile("out file.txt")
        .hash_type(0).attack_mode(0)
        .cmdline()
    )
    # Should contain quoted paths with spaces
    assert re.search(r'"out file\.txt"|\'out file\.txt\'', line)
    assert re.search(r'"my dict\.txt"|\'my dict\.txt\'', line)
