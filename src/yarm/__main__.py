"""Command-line interface."""
import importlib.resources as pkg_resources
import sys
from typing import Any
from typing import Optional

import click


default_config_file: str = "report.yaml"
dir_templates: str = "templates"
template_config_file: str = f"{dir_templates}/{default_config_file}"


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
def new() -> None:
    """Initialize a new yarm project.

    This will create a new config file and open it in your default editor.
    """
    # TODO Allow config option to override.
    config_file: str = default_config_file
    # Do not use pkg_resources.path; it causes problems with testing on python < 3.10
    default_config: str = pkg_resources.read_text(
        f"yarm.{dir_templates}", default_config_file
    )
    with open(config_file, "wt") as new_config:
        new_config.write(default_config)
    new_config.close()
    click.echo("new")
    sys.exit(0)


if __name__ == "__main__":
    cli(prog_name="yarm")  # pylint: disable=E1120 # pragma: no cover
