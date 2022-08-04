#!/usr/bin/env python3
"""Test console.py."""

import click.testing
import pytest

from yarm import console


@pytest.fixture
def runner() -> click.testing.CliRunner:
    """Initialize CliRunner."""
    return click.testing.CliRunner()


def test_main_succeeds(runner: click.testing.CliRunner) -> None:
    """It exits with a status code of zero."""
    result = runner.invoke(console.main)
    assert result.exit_code == 0
