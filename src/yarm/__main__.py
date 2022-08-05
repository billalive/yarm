"""Command-line interface."""
import importlib.resources as pkg_resources
import os
import sys
from typing import Any
from typing import Optional

import click


default_config_file: str = "report.yaml"
dir_templates: str = "templates"
template_config_file: str = f"{dir_templates}/{default_config_file}"
msg_abort: str = "Aborted."
msg_success: str = "Success!"
msg_warn: str = "Warning:"
color_error: str = "red"
color_success: str = "bright_green"
color_warn: str = "bright_yellow"


@click.group(invoke_without_command=True)
@click.version_option()
@click.pass_context
def cli(ctx: Optional[click.Context]) -> Any:
    """yarm: Yet Another Report Maker."""
    if ctx is not None:  # pragma: no branch
        if ctx.invoked_subcommand is None:
            welcome: str = f"""yarm: Yet Another Report Maker.

    Import CSV or XLSX files, run queries, output reports as CSV or XLSX.

    No config file found. (Default: {default_config_file})

    Please either:
        - Supply a config file: yarm -c CONFIG.yaml
        - Or create a new config file: yarm new

    For more options:
        yarm --help
    """
            click.echo(welcome)
        else:
            pass


@cli.command()
@click.option(
    "--edit/--no-edit",
    "-e/-E",
    default=True,
    show_default=True,
    help="Open new config file in your default editor?",
)
@click.option(
    "--force/--no-force",
    "-f/-F",
    default=False,
    show_default=True,
    help="Force overwrite if config file already exists?",
)
def new(edit: Any, force: Any) -> None:
    """Initialize a new yarm project.

    This will create a new config file and, by default,
    open the new file in your default editor.
    """
    # TODO Allow config option to override.
    config_file: str = default_config_file
    # Do not use pkg_resources.path; it causes problems with testing on python < 3.10
    default_config: str = pkg_resources.read_text(
        f"yarm.{dir_templates}", default_config_file
    )
    if os.path.isfile(config_file):
        if not force:
            abort(f"Config file already exists: {config_file}")
        else:
            warn(f"Detected --force, overwriting existing config file: {config_file}")

    with open(config_file, "wt") as new_config:
        new_config.write(default_config)
    new_config.close()

    if edit:
        click.edit(filename=config_file)
    msg = f"""New config file written to: {config_file}

To run this report, type:
    """
    if config_file == default_config_file:
        msg += "yarm"
    else:
        msg += f"yarm -c {config_file}"
    success(msg)


def warn(msg: str) -> None:
    """Show warning, but proceed."""
    click.secho(msg_warn, fg=color_warn, nl=False, bold=True)
    click.echo(" ", nl=False)
    click.echo(msg)
    return


def abort(msg: str) -> None:
    """Abort with error message and status 1."""
    click.secho(msg_abort, fg=color_error, nl=False, bold=True)
    click.echo(" ", nl=False)
    click.echo(msg)
    sys.exit(1)


def success(msg: str) -> None:
    """End with success message and status 0."""
    click.secho(msg_success, fg=color_success, nl=False, bold=True)
    click.echo(" ", nl=False)
    click.echo(msg)


if __name__ == "__main__":
    cli(prog_name="yarm")  # pylint: disable=E1120 # pragma: no cover
