import subprocess
from pathlib import Path


def run_make(makefile: Path, args):
    subprocess.run(["make", "-f", makefile.resolve(), *args])
