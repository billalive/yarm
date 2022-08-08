#!/usr/bin/env python3

"""Helper functions."""

import sys

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


def abort(msg: str) -> None:
    """Abort with error message and status 1."""
    s = Settings()
    click.secho(s.MSG_ABORT, fg=s.COLOR_ERROR, nl=False, bold=True)
    click.echo(" ", nl=False)
    click.echo(msg)
    sys.exit(1)


def success(msg: str) -> None:
    """End with success message and status 0."""
    s = Settings()
    click.secho(s.MSG_SUCCESS, fg=s.COLOR_SUCCESS, nl=False, bold=True)
    click.echo(" ", nl=False)
    click.echo(msg)


def load_yaml_file(input_file: str) -> YAML:
    """Read YAML file into strictyaml."""
    s = Settings()
    try:
        return load(Path(input_file).read_text())
    except YAMLError as err:
        abort(f"{s.MSG_INVALID_CONFIG_BAD_YAML}\nFile: {input_file}\n{err}")
        sys.exit()
    except OSError as err:
        abort(f"{s.MSG_COULDNT_OPEN_YAML}\n{err}")
        sys.exit()


def echo_verbose(msg: str, verbose_level: int = 1) -> bool:
    """Show message if args.verbose is >= than verbose_level."""
    # FIXME args_verbose should be actual argument.
    args_verbose: int = 1
    if args_verbose >= verbose_level:
        print(msg)
    return True
