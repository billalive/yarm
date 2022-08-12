#!/usr/bin/env python3

"""Helper functions."""

import sys
from typing import Any

import click
from path import Path

# from strictyaml import Int
# from strictyaml import Map
# from strictyaml import Seq
# from strictyaml import Str
from strictyaml import YAMLError
from strictyaml import load
from strictyaml.representation import YAML

from yarm.settings import Settings


# from typing import Dict


def warn(msg: str) -> None:
    """Show warning, but proceed."""
    s = Settings()
    click.secho(s.MSG_WARN, fg=s.COLOR_WARN, nl=False, bold=True)
    click.echo(" ", nl=False)
    click.echo(msg)
    return


def abort(msg: str, error: str = None, file_path: str = None):
    """Abort with error message and status 1.

    Args:
        msg: (str)  message
        error: (str, optional)  error
        file_path: (str, optional)  file with this error
    """
    s = Settings()
    # TODO Use err=True to print to stderr?
    click.secho(s.MSG_ABORT, fg=s.COLOR_ERROR, nl=False, bold=True)
    click.echo(" ", nl=False)
    click.echo(msg)
    if file_path is not None:
        click.secho("In file: ", nl=False)
        click.secho(file_path, fg=s.COLOR_DATA, bold=True)
    if error is not None:
        click.echo("Error: ", nl=False)
        click.secho(error, fg=s.COLOR_ERROR)
    # FIXME sys.exit(1) appears to break coverage, resulting in many lines
    # that are tested showing up as not tested. But this may be a bug in coverage:
    # https://github.com/nedbat/coveragepy/issues/1433
    sys.exit(1)


def success(msg: str) -> None:
    """Show success message.

    Args:
        msg: (str)  message

    """
    s = Settings()
    click.secho(s.MSG_SUCCESS, fg=s.COLOR_SUCCESS, nl=False, bold=True)
    click.echo(" ", nl=False)
    click.echo(msg)


def load_yaml_file(input_file: str, schema: Any) -> YAML:
    """Read YAML file into strictyaml, and validate against a schema.

    Args:
        input_file (str): path to YAML file
        schema: strictyaml schema

    Returns:
        YAML object
    """
    s = Settings()
    try:
        return load(Path(input_file).read_text(), schema)
    except YAMLError as error:
        abort(s.MSG_INVALID_YAML, error=error, file_path=input_file)
    except FileNotFoundError:
        abort(s.MSG_CONFIG_FILE_NOT_FOUND, file_path=input_file)


def msg_with_data(msg: str, data: str):
    """Show message with accompanying data."""
    s = Settings()
    msg += ": "
    click.echo(msg, nl=False)
    click.secho(data, fg=s.COLOR_DATA)


def echo_verbose(msg: str, verbose_level: int = 1) -> bool:
    """Show message if args.verbose is >= than verbose_level."""
    # FIXME args_verbose should be actual argument.
    args_verbose: int = 1  # pragma: no cover
    if args_verbose >= verbose_level:  # pragma: no cover
        print(msg)  # pragma: no cover
    return True  # pragma: no cover
