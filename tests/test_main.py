"""Test cases for the __main__ module."""
import importlib.resources as pkg_resources
from typing import Any

import pytest
from click.testing import CliRunner

from yarm import __main__
from yarm.__main__ import cli
from yarm.__main__ import default_config_file
from yarm.__main__ import dir_templates


# import os


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


@pytest.fixture
def mock_click_edit(monkeypatch):
    """When 'testing' click.edit() simply return True for click.edit() tests.

    This is unfortunate, but click.edit() is used sparingly by yarm,
    and testing it thoroughly would presently be difficult:
    https://github.com/pallets/click/issues/1720
    """

    def fake_click_edit(*args, **kwargs):
        return True

    # monkeypatch.setattr(click, "edit", fake_edit)
    monkeypatch.setattr("click.edit", fake_click_edit)


def test_new_noargs_succeeds(runner: CliRunner, mock_click_edit: Any) -> None:
    """It exits with a status code of zero."""
    with runner.isolated_filesystem():
        result = runner.invoke(cli, ["new"])
        assert result.exit_code == 0


def test_new_edit_succeeds(runner: CliRunner, mock_click_edit: Any) -> None:
    """It exits with a status code of zero."""
    with runner.isolated_filesystem():
        result = runner.invoke(cli, ["new", "--edit"])
        assert result.exit_code == 0
