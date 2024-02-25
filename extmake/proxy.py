import subprocess
from pathlib import Path


def run_make(makefile: Path, args) -> subprocess.CompletedProcess:
    return subprocess.run(
        args=["make", "-f", makefile.resolve(), *args],
        bufsize=0,
    )
