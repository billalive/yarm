"""Command-line interface."""
import click


@click.command()
@click.version_option()
def main() -> None:
    """yarm: Yet Another Report Maker."""
    click.echo("Welcome to yarm!")


if __name__ == "__main__":
    main(prog_name="yarm")  # pragma: no cover
