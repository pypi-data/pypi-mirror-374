"""Provides functions for submitting models as jobs.

.. codeauthor:: David Zwicker <david.zwicker@ds.mpg.de>
"""

from __future__ import annotations

import errno
import itertools
import json
import logging
import os
import shlex
import subprocess as sp
import sys
import warnings
from collections.abc import Iterable
from pathlib import Path
from typing import Any, Literal

from tqdm.auto import tqdm

from .. import Parameter
from ..config import Config


def escape_string(obj) -> str:
    """Escape a string for the command line."""
    return shlex.quote(str(obj))


def ensure_directory_exists(folder: str | Path) -> None:
    """Creates a folder if it not already exists."""
    if folder == "":
        return
    try:
        Path(folder).mkdir(parents=True)
    except OSError as err:
        if err.errno != errno.EEXIST:
            raise


DEFAULT_CONFIG = [
    Parameter(
        "python_bin",
        "sys.executable",
        str,
        "Path to the python executable to be used. The special value `sys.executable` "
        "uses the value returned by `sys.executable`.",
    ),
    Parameter("num_threads", 1, int, "The number of threads to be used"),
    Parameter(
        "method",
        "qsub",
        str,
        "The job submission method.",
        choices=["background", "foreground", "qsub", "srun"],
    ),
    Parameter(
        "partition", "", str, "The partition to which the job will be submitted."
    ),
]


def get_config(
    config: str | dict[str, Any] | None = None, *, load_user_config: bool = True
) -> Config:
    """Create the job configuration.

    Args:
        config (str or dict):
            Configuration settings that will be used to update the default config
        load_user_config (bool):
            Determines whether the file `~/.modelrunner` is loaded as a YAML document to
            provide user-defined settings.

    Returns:
        :class:`~modelrunner.config.Config`: the established configuration
    """
    c = Config(DEFAULT_CONFIG)

    if load_user_config:
        path = Path.home() / ".modelrunner"
        if path.is_file():
            c.load(path)

    if isinstance(config, str):
        c.update(json.loads(config))
    elif config is not None:
        c.update(config)
    return c


def get_job_name(base: str, args: dict[str, Any] | None = None, length: int = 7) -> str:
    """Create a suitable job name.

    Args:
        base (str):
            The stem of the job name
        args (dict):
            Parameters to include in the job name
        length (int):
            Length of the abbreviated parameter name

    Returns:
        str: A suitable job name
    """
    if args is None:
        args = {}

    res = base[:-1] if base.endswith("_") else base
    for name, value in args.items():
        if hasattr(value, "__iter__"):
            value_str = "_".join(f"{v:g}" for v in value)
        else:
            value_str = f"{value:g}"
        res += f"_{name.replace('_', '')[:length].upper()}_{value_str}"
    return res


OverwriteStrategyType = Literal[
    "error", "warn_skip", "silent_skip", "overwrite", "silent_overwrite"
]


def submit_job(
    script: str | Path,
    output: str | Path | None = None,
    name: str = "job",
    parameters: str | dict[str, Any] | None = None,
    config: str | dict[str, Any] | None = None,
    *,
    log_folder: str | Path | None = None,
    method: str = "auto",
    use_modelrunner: bool = True,
    template: str | Path | None = None,
    overwrite_strategy: OverwriteStrategyType = "error",
    **kwargs,
) -> tuple[str, str]:
    """Submit a script to the cluster queue.

    Args:
        script (str of :class:`~pathlib.Path`):
            Path to the script file, which contains the model
        output (str of :class:`~pathlib.Path`):
            Path to the output file, where all the results are saved
        name (str):
            Name of the job
        parameters (str or dict):
            Parameters for the script, either as a python dictionary or a string
            containing a JSON-encoded dictionary.
        config (str or dict):
            Configuration for the job, which determines how the job is run. Can be either
            a python dictionary or a string containing a JSON-encoded dictionary.
        log_folder (str of :class:`~pathlib.Path`):
            Path to the logging folder. If omitted, the default of the template is used,
            which typically sends data to stdout for local scripts (which is thus
            captured and returned by this function) or writes log files to the current
            working directory for remote jobs.
        method (str):
            Specifies the submission method. Currently `background`, `foreground`,
            'srun', and `qsub` are supported. The special value `auto` reads the method
            from the `config` argument.
        use_modelrunner (bool):
            If True, `script` is envoked with the modelrunner library, e.g. by calling
            `python -m modelrunner {script}`.
        template (str of :class:`~pathlib.Path`):
            Jinja template file for submission script. If omitted, a standard template
            is chosen based on the submission method.
        overwrite_strategy (str):
            Determines what to do when files already exist. Possible options include
            `error`, `warn_skip`, `silent_skip`, `overwrite`, and `silent_overwrite`.

    Returns:
        tuple: The result `(stdout, stderr)` of the submission call. These two strings
            can contain the output from the actual scripts that is run when `log_folder`
            is `None`.
    """
    from jinja2 import Template

    logger = logging.getLogger("modelrunner.submit_job")

    # prepare job configuration
    configuration = get_config(config)
    if kwargs:
        # deprecated since 2024-01-03
        warnings.warn("kwargs are deprecated. Use `config` instead", DeprecationWarning)
        for k, v in kwargs.items():
            configuration[k] = v
    if configuration["python_bin"] == "sys.executable":
        configuration["python_bin"] = sys.executable

    # determine the submission method
    if method == "auto":
        method = configuration["method"]

    # load the correct template
    if template is None:
        template_path = Path(__file__).parent / "templates" / (method + ".jinja")
    else:
        template_path = Path(template)
    logger.info("Load template `%s`", template_path)
    with template_path.open() as fp:
        script_template = fp.read()

    # prepare submission script
    script_args: dict[str, Any] = {
        "PACKAGE_PATH": Path(__file__).parents[2],
        "JOB_NAME": name,
        "MODEL_FILE": escape_string(script),
        "USE_MODELRUNNER": use_modelrunner,
        "CONFIG": configuration,
    }
    if log_folder is not None:
        ensure_directory_exists(log_folder)
        script_args["LOG_FOLDER"] = log_folder

    # add the parameters to the job arguments
    job_args = []
    if parameters is not None and len(parameters) > 0:
        if isinstance(parameters, dict):
            parameters_json = json.dumps(parameters)
        elif isinstance(parameters, str):
            parameters_json = parameters
        else:
            raise TypeError("Parameters need to be given as a string or a dict")
        job_args.append(f"--json {escape_string(parameters_json)}")
        script_args["PARAMETERS"] = parameters  # allow using parameters in job script

    logger.debug("Job arguments: `%s`", job_args)

    # add the output folder to the job arguments
    if output:
        output = Path(output)
        if output.is_file():
            # output is an existing file, so we need to decide what to do with this
            if overwrite_strategy == "error":
                raise RuntimeError(f"Output file `{output}` already exists")
            elif overwrite_strategy == "warn_skip":
                warnings.warn(f"Output file `{output}` already exists")
                return "", f"Output file `{output}` already exists"  # do nothing
            elif overwrite_strategy == "silent_skip":
                return "", f"Output file `{output}` already exists"  # do nothing
            elif overwrite_strategy == "overwrite":
                warnings.warn(f"Output file `{output}` will be overwritten")
            elif overwrite_strategy == "silent_overwrite":
                pass
            else:
                raise NotImplementedError(f"Unknown strategy `{overwrite_strategy}`")

            # delete old output
            output.unlink()

        # check whether output points to a directory or whether this should be a file
        if output.is_dir():
            script_args["OUTPUT_FOLDER"] = shlex.quote(str(output))
        else:
            script_args["OUTPUT_FOLDER"] = shlex.quote(str(output.parent))
            job_args.append(f"--output {escape_string(output)}")

    else:
        # if `output` is not specified, save data to current directory
        script_args["OUTPUT_FOLDER"] = "."
    script_args["JOB_ARGS"] = " ".join(job_args)

    # replace parameters in submission script template
    script_content = Template(script_template).render(script_args)
    logger.debug("Script: `%s`", script_content)

    if method in {"qsub", "srun"}:
        # submit job to queue
        proc = sp.Popen(
            [method],
            stdin=sp.PIPE,
            stdout=sp.PIPE,
            stderr=sp.PIPE,
            universal_newlines=True,
        )

    elif method == "foreground":
        # run job locally in the foreground, blocking further calls
        proc = sp.Popen(
            ["bash"],
            stdin=sp.PIPE,
            stdout=sp.PIPE,
            stderr=sp.PIPE,
            universal_newlines=True,
            bufsize=0,  # write output immediately
        )

    elif method == "background":
        # run job locally in the background
        proc = sp.Popen(
            ["bash"],
            stdin=sp.PIPE,
            stdout=sp.PIPE,
            stderr=sp.PIPE,
            universal_newlines=True,
        )

    else:
        raise ValueError(f"Unknown submit method `{method}`")

    return proc.communicate(script_content)


def submit_jobs(
    script: str | Path,
    output_folder: str | Path,
    name_base: str = "job",
    parameters: str | dict[str, Any] | None = None,
    config: str | dict[str, Any] | None = None,
    *,
    output_format: str = "hdf",
    list_params: Iterable[str] | None = None,
    **kwargs,
) -> int:
    """Submit many jobs of the same script with different parameters to the cluster.

    Args:
        script (str of :class:`~pathlib.Path`):
            Path to the script file, which contains the model
        output_folder (str of :class:`~pathlib.Path`):
            Path to the output folder, where all the results are saved
        name_base (str):
            Base name of the job. An automatic name is generated on this basis.
        parameters (str or dict):
            Parameters for the script, either as a python dictionary or a string
            containing a JSON-encoded dictionary. All combinations of parameter values
            that are iterable and not strings and not part of `keep_list` are submitted
            as separate jobs.
        config (str or dict):
            Configuration for the job, which determines how the job is run. Can be either
            a python dictionary or a string containing a JSON-encoded dictionary.
        output_format (str):
            File extension determining the output format
        list_params (list):
            List of parameters that are meant to be lists. They will be submitted as
            individual parameters and not iterated over to produce multiple jobs.
        **kwargs:
            All additional parameters are forwarded to :func:`submit_job`.

    Returns:
        int: The number of jobs that have been submitted
    """
    if parameters is None:
        parameter_dict = {}
    elif isinstance(parameters, str):
        parameter_dict = json.loads(parameters)
    else:
        parameter_dict = parameters
    if list_params is None:
        list_params = set()

    # detect varying parameters
    params, p_vary = {}, {}
    for name, value in parameter_dict.items():
        if (
            hasattr(value, "__iter__")
            and not isinstance(value, str)
            and name not in list_params
        ):
            p_vary[name] = value
        else:
            params[name] = value

    # build the list of all varying arguments
    p_vary_list = [
        dict(zip(p_vary.keys(), values))
        for values in itertools.product(*p_vary.values())
    ]

    if not output_format.startswith("."):
        output_format = "." + output_format

    # submit jobs with all parameter variations
    for p_job in tqdm(p_vary_list):
        params.update(p_job)
        name = get_job_name(name_base, p_job)
        output = Path(output_folder) / f"{name}{output_format}"
        submit_job(
            script, output=output, name=name, parameters=params, config=config, **kwargs
        )

    return len(p_vary_list)
