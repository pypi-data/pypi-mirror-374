"""
.. codeauthor:: David Zwicker <david.zwicker@ds.mpg.de>
"""

import os
import subprocess as sp
import sys
from pathlib import Path

import pytest

PACKAGEPATH = Path(__file__).resolve().parents[1]
EXAMPLE_PATH = PACKAGEPATH / "examples"
assert EXAMPLE_PATH.is_dir()


@pytest.mark.no_cover
@pytest.mark.skipif(sys.platform == "win32", reason="Assumes unix setup")
@pytest.mark.parametrize("path", EXAMPLE_PATH.glob("*.py"))
def test_examples(path, tmp_path):
    """Runs an example script given by path."""
    # prepare environment
    env = os.environ.copy()
    env["PYTHONPATH"] = str(PACKAGEPATH) + ":" + env.get("PYTHONPATH", "")

    # run example in temporary folder since it might create data files
    proc = sp.Popen(
        [sys.executable, path], cwd=tmp_path, env=env, stdout=sp.PIPE, stderr=sp.PIPE
    )
    outs, errs = proc.communicate(timeout=30)

    msg = f"Script `{path}` failed with following output:"
    if outs:
        msg = f"{msg}\nSTDOUT:\n{outs}"
    if errs:
        msg = f"{msg}\nSTDERR:\n{errs}"

    assert proc.returncode <= 0, msg
