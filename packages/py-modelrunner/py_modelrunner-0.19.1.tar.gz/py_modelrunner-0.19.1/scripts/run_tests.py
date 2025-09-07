#!/usr/bin/env python3

from __future__ import annotations

import argparse
import os
import subprocess as sp
import sys
from pathlib import Path

PACKAGE = "modelrunner"  # name of the package that needs to be tested
PACKAGE_PATH = Path(__file__).resolve().parents[1]  # base path of the package


def test_codestyle(*, verbose: bool = True):
    """Run the codestyle tests.

    Args:
        verbose (bool): Whether to do extra output
    """
    for folder in [PACKAGE, "examples"]:
        if verbose:
            print(f"Checking codestyle in folder {folder}...")
        path = PACKAGE_PATH / folder

        # check format
        sp.check_call(["ruff", "check", path])


def test_types(*, report: bool = False, verbose: bool = True):
    """Run mypy to check the types of the python code.

    Args:
        report (bool): Whether to write a report
        verbose (bool): Whether to do extra output
    """
    if verbose:
        print(f"Checking types in the {PACKAGE} package...")

    args = [
        sys.executable,
        "-m",
        "mypy",
        "--config-file",
        PACKAGE_PATH / "pyproject.toml",
    ]

    if report:
        folder = PACKAGE_PATH / "tests" / "mypy-report"
        if verbose:
            print(f"Writing report to `{folder}`")
        args.extend(
            ["--no-incremental", "--linecount-report", folder, "--html-report", folder]
        )
    else:
        # do not create a report
        args.append("--pretty")

    args.extend(["--package", PACKAGE])

    sp.run(args, cwd=PACKAGE_PATH)


def run_unit_tests(
    parallel: bool = False,
    coverage: bool = False,
    no_numba: bool = False,
    pattern: str = None,
    pytest_args: list[str] = None,
) -> int:
    """Run the unit tests.

    Args:
        parallel (bool): Whether to use multiple processors
        coverage (bool): Whether to determine the test coverage
        no_numba (bool): Whether to disable numba jit compilation
        pattern (str): A pattern that determines which tests are ran
        pytest_args (list of str):
            Additional arguments forwarded to py.test. For instance ["--maxfail=1"]
            fails tests early.

    Returns:
        int: The return code indicating success or failure
    """
    # modify current environment
    if pytest_args is None:
        pytest_args = []
    env = os.environ.copy()
    env["MPLBACKEND"] = "agg"
    if no_numba:
        env["NUMBA_DISABLE_JIT"] = "1"
    else:
        env["NUMBA_WARNINGS"] = "1"
        env["NUMBA_BOUNDSCHECK"] = "1"

    # build the arguments string
    args = [
        sys.executable,
        "-m",
        "pytest",  # run pytest module
        "-c",
        "pyproject.toml",  # locate the configuration file
        "-rs",  # show summary of skipped tests
        "-rw",  # show summary of warnings raised during tests
    ]

    # run tests using multiple cores?
    if parallel:
        args.extend(["-n", str(os.cpu_count()), "--durations=10"])

    # run only a subset of the tests?
    if pattern is not None:
        args.extend(["-k", str(pattern)])

    # add coverage attributes?
    if coverage:
        args.extend(
            [
                "--cov-config=pyproject.toml",
                "--cov-report",
                "html:scripts/coverage",
                f"--cov={PACKAGE}",
            ]
        )

    args.extend(pytest_args)

    # specify the package to run
    args.append("tests")

    # actually run the test
    retcode = sp.run(args, env=env, cwd=PACKAGE_PATH).returncode

    # delete intermediate coverage files, which are sometimes left behind
    if coverage:
        for p in Path("..").glob(".coverage*"):
            p.unlink()

    return retcode


def main():
    """The main program controlling the tests."""
    # parse the command line arguments
    parser = argparse.ArgumentParser(
        description=f"Run tests of the `{PACKAGE}` package.",
        epilog="All test categories are run if no specific categories are selected.",
    )

    # add the basic tests that need to be run
    group = parser.add_argument_group("Test categories")
    group.add_argument(
        "-s", "--style", action="store_true", default=False, help="Test code style"
    )
    group.add_argument(
        "-t", "--types", action="store_true", default=False, help="Test object types"
    )
    group.add_argument(
        "-u", "--unit", action="store_true", default=False, help="Run unit tests"
    )

    # set additional arguments
    group = parser.add_argument_group("Additional arguments")
    group.add_argument(
        "-q",
        "--quite",
        action="store_true",
        default=False,
        help="Suppress output from the script",
    )
    group.add_argument(
        "--coverage",
        action="store_true",
        default=False,
        help="Record test coverage of unit tests",
    )
    group.add_argument(
        "--parallel",
        action="store_true",
        default=False,
        help="Use multiprocessing",
    )
    group.add_argument(
        "--no_numba",
        action="store_true",
        default=False,
        help="Do not use just-in-time compilation of numba",
    )
    group.add_argument(
        "--pattern",
        metavar="PATTERN",
        type=str,
        help="Only run tests with this pattern",
    )
    group.add_argument(
        "--report",
        action="store_true",
        default=False,
        help="Write a report of the results",
    )

    # set py.test arguments
    group = parser.add_argument_group(
        "py.test arguments",
        description="Additional arguments separated by `--` are forward to py.test",
    )
    group.add_argument("pytest_args", nargs="*", help=argparse.SUPPRESS)

    # parse the command line arguments
    args = parser.parse_args()
    run_all = not (args.style or args.types or args.unit)

    # run the requested tests
    if run_all or args.style:
        test_codestyle(verbose=not args.quite)
    if run_all or args.types:
        test_types(report=args.report, verbose=not args.quite)
    if run_all or args.unit:
        run_unit_tests(
            coverage=args.coverage,
            parallel=args.parallel,
            no_numba=args.no_numba,
            pattern=args.pattern,
            pytest_args=args.pytest_args,
        )


if __name__ == "__main__":
    main()
