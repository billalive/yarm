"""Command-line interface."""
# pylint: disable=invalid-name

import importlib.resources as pkg_resources
import os
import sys
from typing import Any
from typing import Optional

# Dependencies
#
# If your distribution does not include openpyxl with pandas, you may need
# to install python-openpyxl separately.
import click

from yarm.helpers import abort
from yarm.helpers import success
from yarm.helpers import warn
from yarm.helpers import yaml_to_dict
from yarm.settings import Settings
from yarm.validate import validate_config


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
        f"{s.PKG}.{s.DIR_TEMPLATES}", s.DEFAULT_CONFIG_FILE
    )
    if os.path.isfile(config_file):
        if not force:
            abort(f"Config file already exists: {config_file}")
        else:
            warn(f"Detected --force, overwriting existing config file: {config_file}")

    with open(config_file, "wt") as new_config:
        new_config.write(default_config)

    if edit:
        click.edit(filename=config_file)
    msg = f"""New config file written to: {config_file}

To run this report, type:
    """
    if config_file == s.DEFAULT_CONFIG_FILE:
        msg += "yarm run"
    else:
        msg += f"yarm run -c {config_file}"
    success(msg)


if __name__ == "__main__":
    cli(prog_name="yarm")  # pylint: disable=E1120 # pragma: no cover
