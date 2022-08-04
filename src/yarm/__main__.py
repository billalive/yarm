"""Command-line interface."""
import click


@click.command()
@click.version_option()
def main() -> None:
    """yarm: Yet Another Report Maker."""
    welcome: str = """yarm: Yet Another Report Maker.

Import CSV or XLSX files, run queries, output reports as CSV or XLSX.

No config file found. Please either:
    - Supply a config file with -c CONFIG.yaml
    - Or create a new config file with -n

For more options:
    yarm --help"""
    click.echo(welcome)


if __name__ == "__main__":
    main(prog_name="yarm")  # pragma: no cover
