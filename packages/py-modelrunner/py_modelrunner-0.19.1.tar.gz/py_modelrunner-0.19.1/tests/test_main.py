"""
.. codeauthor:: David Zwicker <david.zwicker@ds.mpg.de>
"""

import os
import subprocess as sp
import sys
from pathlib import Path

PACKAGEPATH = Path(__file__).parents[1].resolve()
assert PACKAGEPATH.is_dir()


def test_empty_main():
    """Run a script (with potential arguments) and collect stdout."""
    # prepare environment
    env = os.environ.copy()
    env["PYTHONPATH"] = str(PACKAGEPATH) + ":" + env.get("PYTHONPATH", "")

    # run example in temporary folder since it might create data files
    cmd_args = (sys.executable, "-m", "modelrunner")
    proc = sp.Popen(cmd_args, env=env, stdout=sp.PIPE, stderr=sp.PIPE)
    _, errs = proc.communicate(timeout=30)
    assert b"Require job script as first argument" in errs


def test_main():
    """Test the __main__ module."""
    # prepare environment
    env = os.environ.copy()
    env["PYTHONPATH"] = str(PACKAGEPATH) + ":" + env.get("PYTHONPATH", "")

    # run example in temporary folder since it might create data files
    path = PACKAGEPATH / "tests" / "run" / "scripts" / "function.py"
    cmd_args = (sys.executable, "-m", "modelrunner", path)
    proc = sp.Popen(cmd_args, env=env, stdout=sp.PIPE, stderr=sp.PIPE)
    _, errs = proc.communicate(timeout=30)

    assert errs == b""
