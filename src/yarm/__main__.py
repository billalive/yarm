"""Command-line interface."""
from typing import Any
from typing import Optional

import click


default_config_file: str = "report.yaml"


@click.group(invoke_without_command=True)
@click.version_option()
@click.pass_context
def cli(ctx: Optional[click.Context]) -> Any:
    """yarm: Yet Another Report Maker."""
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
    click.echo("new")


if __name__ == "__main__":
    cli(prog_name="yarm")  # pragma: no cover
