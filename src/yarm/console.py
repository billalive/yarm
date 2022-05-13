#!/usr/bin/env python3

import click

from . import __version__


@click.command()
@click.version_option(version=__version__)
def main():
    """yarm: yet another report maker"""
    click.echo("Welcome to yarm.")
