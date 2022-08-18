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
from strictyaml.ruamel.scanner import ScannerError

from yarm.settings import Settings


# from typing import Dict


def warn(msg: str) -> None:
    """Show warning, but proceed."""
    s = Settings()
    click.secho(s.MSG_WARN, fg=s.COLOR_WARN, nl=False, bold=True)
    click.echo(" ", nl=False)
    click.echo(msg)
    return


def abort(
    msg: str, error: str = None, file_path: str = None, data: str = None, ps: str = None
):
    """Abort with error message and status 1.

    Args:
        msg: (str)  message
        error: (str, optional)  error
        file_path: (str, optional)  file with this error, display on separate line
        data: (str, optional) data to display after msg
        ps: (str, optional) final postscript to add at end of message.
    """
    s = Settings()
    # TODO Use err=True to print to stderr?
    click.secho(s.MSG_ABORT, fg=s.COLOR_ERROR, nl=False, bold=True)
    click.echo(" ", nl=False)
    if data:
        click.echo(msg, nl=False)
        click.echo(": ", nl=False)
        click.secho(data, fg=s.COLOR_DATA, bold=True)
    else:
        click.echo(msg)
    if file_path:
        click.secho("In file: ", nl=False)
        click.secho(file_path, fg=s.COLOR_DATA, bold=True)
    if error:
        click.echo("Error: ", nl=False)
        click.secho(error, fg=s.COLOR_ERROR)
    if ps:
        click.echo(ps)
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
        abort(s.MSG_INVALID_YAML, error=str(error), file_path=input_file)
    except FileNotFoundError:
        abort(s.MSG_CONFIG_FILE_NOT_FOUND, file_path=input_file)
    except IsADirectoryError:
        abort(f"{s.MSG_DIRECTORY_ERROR} {input_file}")
    except PermissionError:  # pragma: no cover
        abort(f"{s.MSG_PERMISSION_ERROR} (Are you sure this is a file?)\n{input_file}")
    except ScannerError as error:  # pragma: no cover
        # https://github.com/crdoconnor/strictyaml/issues/22
        abort(s.MSG_INVALID_YAML_SCANNER, error=str(error), file_path=input_file)


def msg(msg: str, verbose: int = 0):
    """Show message.

    By default, does not require -v flag.

    Args:
        msg (str): message to display
        verbose (int): (optional) verbosity level required to show this message.

    """
    if verbose_ge(verbose):
        click.echo(msg)


def msg_with_data(msg: str, data: str, verbose: int = 1, indent: int = 0):
    """Show message with accompanying data.

    By default, requires at least one -v flag.

    Args:
        msg (str): message to display
        data (str): data to display after message
        verbose (int): (optional) verbosity level required to show this message.
        indent (int): (optional) number of indents before message
    """
    s = Settings()
    if verbose_ge(verbose):
        msg = (s.MSG_TAB * indent) + msg
        msg += ": "
        click.echo(msg, nl=False)
        click.secho(data, fg=s.COLOR_DATA)


def verbose_ge(verbose: int) -> bool:
    """Return True if verbosity >= verbose."""
    s = Settings()
    ctx = click.get_current_context()
    if ctx.params[s.ARG_VERBOSE] >= verbose:
        return True
    else:
        return False
