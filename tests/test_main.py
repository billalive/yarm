"""Test cases for the __main__ module."""
import importlib.resources as pkg_resources

import pytest
from click.testing import CliRunner

from yarm import __main__
from yarm.__main__ import cli
from yarm.__main__ import default_config_file
from yarm.__main__ import dir_templates


@pytest.fixture
def runner() -> CliRunner:
    """Fixture for invoking command-line interfaces."""
    return CliRunner()


def test_main_succeeds(runner: CliRunner) -> None:
    """It exits with a status code of zero."""
    result = runner.invoke(__main__.cli)
    assert result.exit_code == 0


def test_default_config_template_exists() -> None:
    """The default config file template exists."""
    # assert pkg_resources.is_resource("yarm", template_config_name)
    assert pkg_resources.is_resource(f"yarm.{dir_templates}", default_config_file)


def test_new_succeeds(runner: CliRunner) -> None:
    """It exits with a status code of zero."""
    result = runner.invoke(cli, ["new"])
    assert result.exit_code == 0
