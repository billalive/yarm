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

    Important:
        This function is not normally used directly. Instead, use:

        - :func:`msg`
        - :func:`msg_with_data`
        - :func:`abort`
        - :func:`warn`
        - :func:`success`

    Args:
        msg: Message
        prefix: e.g. :data:`Error`
        prefix_color: e.g. :data:`red`
        error: Error message (**see note**)
        data: Display this data after message, shown on **same** line
        file_path: File associated with this message, shown on **separate** line
        ps: Final postscript to add at end of message
        indent: Number of indents before message

    Note:
        This function expects :data:`error` to be type :data:`str`, but the error
        returned by an :data:`except:` clause may need to be converted with
        :func:`str`.

    """
    s = Settings()
    # TODO Use err=True to print to stderr?
    i = s.MSG_TAB * indent
    # TODO test_msg_options tests this, but coverage doesn't recognize the test.
    if prefix and prefix_color:  # pragma: no cover
        click.secho(i + prefix, fg=prefix_color, nl=False, bold=True)
        click.echo(" ", nl=False)
    if data:
        click.echo(msg, nl=False)
        click.echo(": ", nl=False)
        click.secho(data, fg=s.COLOR_DATA, bold=True)
    else:
        click.echo(i + msg)
    if file_path:
        click.secho(i + "In file: ", nl=False)
        click.secho(file_path, fg=s.COLOR_DATA, bold=True)
    if error:
        click.echo(i + "Error: ", nl=False)
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

    Args:
        msg: Message
        error: Error message (**see note** in :func:`msg_options`)
        data: Display this data after message, shown on **same** line
        file_path: File associated with this message, shown on **separate** line
        ps: Final postscript to add at end of message
        indent: Number of indents before message
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

    Args:
        msg: Message
        error: Error message (**see note** in :func:`msg_options`)
        data: Display this data after message, shown on **same** line
        file_path: File associated with this message, shown on **separate** line
        ps: Final postscript to add at end of message
        indent: Number of indents before message
        suggest_verbose: Verbosity level to pass to :func:`msg_suggest_verbose`
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


def msg_suggest_verbose(suggest_verbose: int):
    """Show message suggesting rerunning with a higher level of verbosity.

    Note:
        This message will only be shown if the verbosity level is set lower
        than :data:`suggest_verbose`.

    Args:
        suggest_verbose: Verbosity level that message will suggest
    """
    s = Settings()
    ctx = click.get_current_context()
    if s.ARG_VERBOSE in ctx.params:
        if ctx.params[s.ARG_VERBOSE] < suggest_verbose:
            msg_verbose = s.MSG_VERBOSITY_PS
            msg_verbose += "-"
            msg_verbose += "v" * suggest_verbose
            # TODO Next lines tested in test_msg_suggest_verbose, but coverage misses.
            if suggest_verbose < s.MAX_VERBOSE:  # pragma: no cover
                msg_verbose += " or -"
                msg_verbose += "v" * (suggest_verbose + 1)
            msg_verbose += "."
            click.echo(msg_verbose)


def success(
    msg: str,
    file_path: str = None,
    data: str = None,
    ps: str = None,
) -> None:
    """Show success message.

    Args:
        msg: Message
        data: Display this data after message, shown on **same** line
        file_path: File associated with this message, shown on **separate** line
        ps: Final postscript to add at end of message
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
    """Read YAML file into :data:`strictyaml`, and validate against a schema.

    Args:
        input_file: path to YAML file
        schema: :data:`strictyaml` schema

    Returns:
        Validated YAML
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

    Note:
        By default, this message will still show even if user did not use
        a :data:`-v` flag.

    Args:
        msg: Message to display
        verbose: Minimum verbosity required to show this message
        indent: Number of indents before message
    """
    s = Settings()
    if verbose_ge(verbose):
        msg = (s.MSG_TAB * indent) + msg
        click.echo(msg)


def msg_with_data(msg: str, data: str, verbose: int = 1, indent: int = 0):
    """Show message with accompanying data.

    Note:
        By default, the message will only be shown if the user used at least
        one :data:`-v` flag.

    Args:
        msg: Message to display
        data: Display this data after message, shown on **same** line
        verbose: Minimum verbosity required to show this message
        indent: Number of indents before message
    """
    s = Settings()
    if verbose_ge(verbose):
        msg = (s.MSG_TAB * indent) + msg
        msg += ": "
        click.echo(msg, nl=False)
        click.secho(data, fg=s.COLOR_DATA)


def verbose_ge(verbose: int) -> bool:
    """Return :data:`True` if verbosity >= :data:`verbose`.

    Args:
        verbose: verbosity level

    Returns:
        True if user used `verbose` or more `-v` flags, otherwise False

    """
    s = Settings()
    ctx = click.get_current_context()
    if ctx.params[s.ARG_VERBOSE] >= verbose:
        return True
    else:
        return False


def overwrite_file(path: str, indent: int = 1) -> bool:
    """Overwrite a file if it exists.

    Note:
        Technically, this function only *removes* the file. The new
        file must be written separately.

    Note:
        If a prompt question is shown, it is not indented.

    Args:
        path: File to overwrite
        indent: Number of indents before message

    Returns:
        True if file existed and was removed, False otherwise
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
    """For each key, if that key is in :data:`config`, show the matching message.

    Important:
        :data:`key_msg` must be a **list** of **tuples** of the form: `(key, message)`.

    .. code-block:: python

        key_msg: list = [
            (s.KEY_INPUT__STRIP, s.MSG_STRIP_WHITESPACE),
            (s.KEY_INPUT__SLUGIFY_COLUMNS, s.MSG_SLUGIFY_COLUMNS),
            (s.KEY_INPUT__LOWERCASE_COLUMNS, s.MSG_LOWERCASE_COLUMNS),
            (s.KEY_INPUT__UPPERCASE_ROWS, s.MSG_UPPERCASE_ROWS),
        ]
        key_show_message(key_msg, config, verbose=1)

    Args:
        key_msg: List of tuples of the form: :data:`(key, message)`
        config: Report configuration
        verbose: Minimum verbosity level required to show this message

    """
    for key, msg_str in key_msg:
        if key in config and config[key][:]:
            msg(msg_str, verbose=verbose)


def show_df(df: DataFrame, data: str, verbose: int = 3):
    """Display a dataframe.

    Args:
        df: Data to display
        data: Display this data after message, shown on **same** line
        verbose: Minimum verbosity level required to show this message

    """
    s = Settings()
    if verbose_ge(verbose):
        print(s.MSG_LINE)
        msg_with_data(s.MSG_SHOW_DF, data=data)
        print(df)
        print(s.MSG_LINE)
