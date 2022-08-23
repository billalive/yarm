#!/usr/bin/env python3

"""Helper functions."""

import os
import sys
from typing import Any
from typing import List
from typing import Tuple

import click
from nob.nob import Nob
from pandas.core.frame import DataFrame
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


def msg_options(
    msg: str,
    prefix: str = None,
    prefix_color: str = None,
    error: str = None,
    file_path: str = None,
    data: str = None,
    ps: str = None,
    indent: int = 0,
):
    """Show a message with various options.

    Args:
        msg: (str)  message
        prefix: (str, optional)  e.g. Error
        prefix_color: (str, optional) e.g. s.COLOR_ERROR
        error: (str, optional)  error
        file_path: (str, optional)  file with this error, display on separate line
        data: (str, optional) data to display after msg
        ps: (str, optional) final postscript to add at end of message.
        indent: (str, optional) indent the message by this many tabs.
    """
    s = Settings()
    # TODO Use err=True to print to stderr?
    if indent > 0:
        click.echo(s.MSG_TAB * indent, nl=False)
    # TODO test_msg_options tests this, but coverage doesn't recognize the test.
    if prefix and prefix_color:  # pragma: no cover
        click.secho(prefix, fg=prefix_color, nl=False, bold=True)
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


def warn(
    msg: str,
    error: str = None,
    file_path: str = None,
    data: str = None,
    ps: str = None,
    indent: int = 0,
) -> None:
    """Show warning, but proceed.

    For args, see message_with_options()
    """
    s = Settings()
    msg_options(
        msg=msg,
        prefix=s.MSG_WARN,
        prefix_color=s.COLOR_WARN,
        error=error,
        file_path=file_path,
        data=data,
        ps=ps,
        indent=indent,
    )
    return


def abort(
    msg: str,
    error: str = None,
    file_path: str = None,
    data: str = None,
    ps: str = None,
    indent: int = 0,
    suggest_verbose: int = 1,
):
    """Abort with error message and status 1.

    For args, see message_with_options()
    """
    s = Settings()

    msg_options(
        msg=msg,
        prefix=s.MSG_ABORT,
        prefix_color=s.COLOR_ERROR,
        error=error,
        file_path=file_path,
        data=data,
        ps=ps,
        indent=indent,
    )

    msg_suggest_verbose(suggest_verbose)
    sys.exit(1)


def msg_suggest_verbose(suggest_verbose):
    """Suggest rerunning with a higher level of verbosity."""
    s = Settings()
    ctx = click.get_current_context()
    if ctx.params[s.ARG_VERBOSE] < suggest_verbose:
        msg_verbose = s.MSG_VERBOSITY_PS
        msg_verbose += "-"
        msg_verbose += "v" * suggest_verbose
        if suggest_verbose < s.MAX_VERBOSE:
            msg_verbose += " or -"
            msg_verbose += "v" * (suggest_verbose + 1)
        msg_verbose += "."
        click.echo(msg_verbose)


def success(
    msg: str,
    prefix: str = None,
    prefix_color: str = None,
    file_path: str = None,
    data: str = None,
    ps: str = None,
) -> None:
    """Show success message.

    For args, see message_with_options()
    """
    s = Settings()
    msg_options(
        msg=msg,
        prefix=s.MSG_SUCCESS,
        prefix_color=s.COLOR_SUCCESS,
        file_path=file_path,
        data=data,
        ps=ps,
    )


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


def msg(msg: str, verbose: int = 0, indent: int = 0):
    """Show message.

    By default, does not require -v flag.

    Args:
        msg (str): message to display
        verbose (int): (optional) verbosity level required to show this message.
        indent (int): (optional) number of indents before message
    """
    s = Settings()
    if verbose_ge(verbose):
        msg = (s.MSG_TAB * indent) + msg
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


def overwrite_file(path: str, indent: int = 1) -> bool:
    """Overwrite a file if it exists.

    (Technically, this function only removes the file.)

    Args:
        path (str): file to overwrite
        indent (int): (optional) indent for "removed file" message.
            Prompt question is not indented.

    Returns:
        (bool) True if file existed and was removed, False otherwise.
    """
    # TODO Should this test whether we are in output/dir?
    # And only overwrite files in that directory?
    s = Settings()

    ctx = click.get_current_context()

    msg_removed: str = s.MSG_REMOVED_FILE

    remove: bool = False
    if os.path.isfile(path):
        if ctx.params[s.ARG_FORCE]:
            remove = True
            msg_removed = s.MSG_REMOVED_FILE_FORCE
        else:
            msg: str = f"{s.MSG_PROMPT}{s.MSG_ASK_OVERWRITE_FILE} {path}?"
            if click.confirm(msg, default=True, abort=False):
                remove = True
            else:
                abort(s.MSG_OVERWRITE_FILE_ABORT, data=path)  # pragma: no cover

        if remove:  # pragma: no cover
            # TODO Why doesn't coverage detect test_overwrite_file()?
            if verbose_ge(2):
                msg_with_data(msg_removed, data=path, indent=indent)
            os.remove(path)
    return remove


def key_show_message(key_msg: List[Tuple[str, str]], config: Nob, verbose: int = 1):
    """For each key, if that key is in config, show message.

    key_msg must be a list of tuples.

    Example:
    key_msg: list = [
        (s.KEY_INPUT__STRIP, s.MSG_STRIP_WHITESPACE),
        (s.KEY_INPUT__SLUGIFY_COLUMNS, s.MSG_SLUGIFY_COLUMNS),
        (s.KEY_INPUT__LOWERCASE_COLUMNS, s.MSG_LOWERCASE_COLUMNS),
        (s.KEY_INPUT__UPPERCASE_ROWS, s.MSG_UPPERCASE_ROWS),
    ]
    key_show_message(key_msg, config, verbose=1)

    """
    for key, msg_str in key_msg:
        if key in config and config[key][:]:
            msg(msg_str, verbose=verbose)


def show_df(df: DataFrame, data: str, verbose: int = 3):
    """Display a dataframe."""
    s = Settings()
    if verbose_ge(verbose):
        print(s.MSG_LINE)
        msg_with_data(s.MSG_SHOW_DF, data=data)
        print(df)
        print(s.MSG_LINE)
