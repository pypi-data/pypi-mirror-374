
def test_help_runs():
    # Just ensure the wrapper starts and shows help without crashing.
    import subprocess, sys
    r = subprocess.run([sys.executable, "-m", "olca2tidas.cli", "--help"], capture_output=True, text=True)
    assert r.returncode == 0
    assert "olca2tidas" in r.stdout
