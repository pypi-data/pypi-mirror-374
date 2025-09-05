import re
import pytest
from pathlib import Path
from Phashcat import hashcat

@pytest.mark.integration
def test_builtin_hashcat_version():
    """
    Run 'hashcat --version' against the bundled binary shipped with the package.
    Accepts either a plain semantic version (e.g., 'v7.1.2') or messages containing 'hashcat'.
    """
    here = Path(__file__).resolve().parents[1] / "Phashcat" / "hashcat"
    bundled_win = here / "hashcat.exe"
    bundled_nix = here / "hashcat"

    if bundled_win.exists():
        binary = str(bundled_win)
    elif bundled_nix.exists():
        binary = str(bundled_nix)
    else:
        pytest.skip("No bundled hashcat binary found")

    result = (
        hashcat(binary=binary)
        .set("--version", True)
        .run(check=False, capture_output=True)
    )

    combined = (result.stdout or "") + (result.stderr or "")
    combined = combined.strip()

    # Accept either: a) contains the word 'hashcat', or b) a version like 'v7.1.2' / '7.1.2'
    ok = ("hashcat" in combined.lower()) or bool(re.search(r"\bv?\d+\.\d+(?:\.\d+)?\b", combined))
    assert ok, f"Unexpected --version output: {combined!r}"
