"""Command-line interface."""
import importlib.resources as pkg_resources
import os
import sys
from typing import Any
from typing import Dict
from typing import Optional

# Dependencies
#
# If your distribution does not include openpyxl with pandas, you may need
# to install python-openpyxl separately.
import click
import yaml


class Settings:
    """Define global settings.

    When you need a setting in a function, make an instance
    of this class. These settings should NOT be changed; treat
    them as constants.
    """

    DEFAULT_CONFIG_FILE: str = "report.yaml"
    DIR_TEMPLATES: str = "templates"
    TEMPLATE_CONFIG_FILE: str = "templates/report.yaml"

    MSG_ABORT: str = "Aborted."
    MSG_SUCCESS: str = "Success!"
    MSG_WARN: str = "Warning:"
    MSG_USAGE: str = "Usage:"

    COLOR_ERROR: str = "red"
    COLOR_SUCCESS: str = "bright_green"
    COLOR_WARN: str = "bright_yellow"

    TEST_CUSTOM_CONFIG_FILE: str = "custom.yaml"
    CMD_RUN = "run"


@click.group(invoke_without_command=True)
@click.version_option()
@click.pass_context
def cli(ctx: Optional[click.Context]) -> Any:
    """yarm: Yet Another Report Maker."""
    s = Settings()
    if ctx is not None:  # pragma: no branch
        if ctx.invoked_subcommand is None:
            welcome: str = f"""yarm: Yet Another Report Maker.

Import CSV or XLSX files, run queries, output reports as CSV or XLSX.

No config file found. (Default: {s.DEFAULT_CONFIG_FILE})

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
    "--config",
    "-c",
    "config_path",
    help="Config file for this project.",
    type=click.Path(exists=True),
)
def run(config_path: str) -> None:
    """Run the report(s)."""
    s = Settings()
    if config_path is None:
        config_path = s.DEFAULT_CONFIG_FILE  # type: ignore[unreachable]
    report_config = yaml_to_dict(config_path)
    validate_config(report_config)
    sys.exit()


def validate_config(config: Dict[Any, Any]) -> Any:
    """Validate config file before running report."""
    # Why no test whether file exists? click() handles this.
    for key in config:
        print(key, config[key])
    return


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
@click.option(
    "--path",
    "-p",
    "custom_config_path",
    help="Custom path for new config file.",
    type=click.Path(exists=False),
)
def new(edit: Any, force: Any, custom_config_path: str) -> None:
    """Initialize a new yarm project.

    This will create a new config file and, by default,
    open the new file in your default editor.
    """
    s = Settings()
    config_file: str = s.DEFAULT_CONFIG_FILE
    if custom_config_path is not None:
        config_file = custom_config_path

    # Do not use pkg_resources.path; it causes problems with testing on python < 3.10
    default_config: str = pkg_resources.read_text(
        f"yarm.{s.DIR_TEMPLATES}", s.DEFAULT_CONFIG_FILE
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
    if config_file == s.DEFAULT_CONFIG_FILE:
        msg += "yarm"
    else:
        msg += f"yarm -c {config_file}"
    success(msg)


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


def yaml_to_dict(input_file: str) -> Dict[Any, Any]:
    """Read YAML file, return dictionary."""
    try:
        with open(input_file, "rb") as yaml_file:
            new_dict: Dict[Any, Any] = yaml.safe_load(yaml_file)
            return new_dict
    except OSError as err:
        abort(f"Could not open YAML file: {err}")
        sys.exit()


if __name__ == "__main__":
    cli(prog_name="yarm")  # pylint: disable=E1120 # pragma: no cover
