import subprocess
from Phashcat import hashcat

def test_run_success(fake_run):
    result = (
        hashcat("h.hash", "d.dict")
        .hash_type(0).attack_mode(0)
        .outfile("out.txt")
        .run(check=True, capture_output=True)
    )
    assert result.returncode == 0
    assert isinstance(result.stdout, str)

def test_run_failure_raises_when_check_true(fake_run):
    fake_run["returncode"] = 2
    try:
        (
            hashcat("h.hash", "d.dict")
            .hash_type(0).attack_mode(0)
            .outfile("out.txt")
            .run(check=True, capture_output=True)
        )
        raised = False
    except subprocess.CalledProcessError:
        raised = True
    assert raised is True

def test_run_failure_does_not_raise_when_check_false(fake_run):
    fake_run["returncode"] = 2
    result = (
        hashcat("h.hash", "d.dict")
        .hash_type(0).attack_mode(0)
        .outfile("out.txt")
        .run(check=False, capture_output=True)
    )
    assert result.returncode == 2
