"""Test cases for the __main__ module."""
# pylint: disable=redefined-outer-name
# pylint: disable=invalid-name
# pylint: disable=import-error


import importlib.resources as pkg_resources
import os
from typing import Any

import pytest
from click.testing import CliRunner

from yarm import __main__
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


def prep_test_config(test_config_file: str) -> None:
    """Prepare test config file for a particular test.

    Several tests need a particular file in place as the config file
    for the test. This helper function sets that up.

    Use this helper function inside other tests.

    With this function, a new test requires:

    - Create the malformed config file in s.DIR_TESTS_DATA
    - In __main__ class Settings, define attributes for:
       - filename for this config file
       - unique error message that this config file should trigger.
    - Then write a test that uses this function.

    For example tests that use this function, see:

    - test_report_aborts_invalid_config_bad_yaml()
    - test_report_aborts_invalid_config_bad_options()
    """
    s = Settings()
    # make sure we have a default config file location.
    assert isinstance(s.DEFAULT_CONFIG_FILE, str)
    # copy in the config file for this test.
    assert pkg_resources.is_resource(f"{s.PKG}.{s.DIR_TESTS_DATA}", test_config_file)
    with open(s.DEFAULT_CONFIG_FILE, "wt") as textfile:
        textfile.write(
            pkg_resources.read_text(f"{s.PKG}.{s.DIR_TESTS_DATA}", test_config_file)
        )
    assert os.path.isfile(s.DEFAULT_CONFIG_FILE)
