#!/usr/bin/env python3
"""Command-line interface."""

import click

from . import __version__


@click.command()
@click.version_option(version=__version__)
def main():
    """yarm: Yet Another Report Maker."""
    click.echo("Welcome to yarm.")
