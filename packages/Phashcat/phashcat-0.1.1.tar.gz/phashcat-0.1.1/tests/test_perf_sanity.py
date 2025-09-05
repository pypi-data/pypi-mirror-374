import time
import pytest
from Phashcat import hashcat

@pytest.mark.perf
def test_value_cmdline_perf_sanity():
    b = hashcat()
    for i in range(200):
        b = b.hash_type(0).attack_mode(3).outfile(f"o{i}.txt").status(True).arg(f"h{i}.hash")
    t0 = time.time()
    _ = b.value()
    t1 = time.time()
    _ = b.cmdline()
    t2 = time.time()
    # Not strict; just make sure we're not egregiously slow
    assert (t1 - t0) < 0.2
    assert (t2 - t1) < 0.3
