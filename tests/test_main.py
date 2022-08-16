"""Test cases for the __main__ module."""
# pylint: disable=redefined-outer-name
# pylint: disable=invalid-name
# pylint: disable=import-error


import importlib.resources as pkg_resources
import inspect
import os
from typing import Any

import pytest
from click.testing import CliRunner

from tests.test_helpers import prep_test_config
from yarm import __main__
from yarm import tests_data
from yarm.__main__ import cli
from yarm.settings import Settings


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
    s = Settings()
    assert pkg_resources.is_resource(
        f"{s.PKG}.{s.DIR_TEMPLATES}", s.DEFAULT_CONFIG_FILE
    )


@pytest.fixture
def mock_click_edit(monkeypatch: Any) -> Any:
    """When 'testing' click.edit() simply return True for click.edit() tests.

    This is unfortunate, but click.edit() is used sparingly by yarm,
    and testing it thoroughly would presently be difficult:
    https://github.com/pallets/click/issues/1720
    """

    def fake_click_edit(
        *args: Any, **kwargs: Any  # pylint: disable=unused-argument
    ) -> Any:
        return True

    monkeypatch.setattr("click.edit", fake_click_edit)


def test_new_noargs_succeeds(
    runner: CliRunner,
    mock_click_edit: Any,  # pylint: disable=unused-argument
) -> None:
    """It exits with a status code of zero."""
    with runner.isolated_filesystem():
        result = runner.invoke(cli, ["new"])
        assert result.exit_code == 0


def test_new_edit_succeeds(
    runner: CliRunner,
    mock_click_edit: Any,  # pylint: disable=unused-argument
) -> None:
    """It exits with a status code of zero."""
    with runner.isolated_filesystem():
        result = runner.invoke(cli, ["new", "--edit"])
        assert result.exit_code == 0


def test_prep_config_copies_files(runner: CliRunner) -> None:
    """Copy test_config_name/ files into testing environment."""
    with runner.isolated_filesystem():
        test_config_name: str = "test_prep_config_copies_files"
        prep_test_config(test_config_name)
        assert os.path.isfile("file1.txt")
        assert os.path.isfile("file2.txt")
        assert not os.path.isfile("does_not_exist.txt")


def test_verbose_levels(runner: CliRunner) -> None:
    """Different messages show at different levels of verbose."""
    s = Settings()
    test_config_name: str = "test_verbose_levels"
    with runner.isolated_filesystem():
        prep_test_config(test_config_name)
        result = runner.invoke(cli, [s.CMD_RUN])
        assert s.MSG_VALIDATING_KEY not in result.output
        assert s.MSG_CONFIG_FILE_VALID not in result.output
        assert result.exit_code == 0
        result = runner.invoke(cli, [s.CMD_RUN, "-v"])
        assert s.MSG_VALIDATING_KEY in result.output
        assert s.MSG_CONFIG_FILE_VALID not in result.output
        assert result.exit_code == 0
        result = runner.invoke(cli, [s.CMD_RUN, "-vv"])
        assert s.MSG_VALIDATING_KEY in result.output
        assert s.MSG_CONFIG_FILE_VALID in result.output
        assert result.exit_code == 0


def test_directory_error(runner: CliRunner) -> None:
    """A directory instead of a file raises the correct error."""
    s = Settings()
    # Try passing tests_data dir as config file.
    # This test took some finessing to get working on Windows.
    dir_tests_data: str = os.path.dirname(inspect.getfile(tests_data))
    result = runner.invoke(cli, [s.CMD_RUN, "-c", dir_tests_data])
    assert result.exit_code == 1
    assert s.MSG_DIRECTORY_ERROR in result.output
