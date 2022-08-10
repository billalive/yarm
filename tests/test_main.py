"""Test cases for the __main__ module."""
# pylint: disable=redefined-outer-name
# pylint: disable=invalid-name
# pylint: disable=import-error


import importlib.resources as pkg_resources
import os
import shutil
from typing import Any

import pytest
from click.testing import CliRunner
from path import Path

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


def prep_test_config(test_config_name: str) -> None:
    """Prepare test config file for a particular test.

    Several tests need a particular file in place as the config file
    for the test. This helper function sets that up.

    Use this helper function inside other tests.

    - Create the malformed config file in s.DIR_TESTS_DATA
      - Name it with only letters, numbers, and undescores.
      - Extension should be ".yaml"

    - Optional: If your test needs any supporting files, create a directory in
      tests_data/ with the same name as test_config_name. When this function is
      called with test_config_name, every file in this dir will also be copied
      into the temporary dir for this test. Note that when the test is run,
      these files will be in the *same* dir as the config file, so set the path
      accordingly in the config file.

    For example tests that use this function, see:

    - test_report_aborts_invalid_config_bad_yaml()
    - test_report_aborts_invalid_config_bad_options()
    - test_validate_config_mistakes()

    Args:
        test_config_name (str): basename of config file, without ".yaml"

    """
    s = Settings()
    # make sure we have a default config file location.
    assert isinstance(s.DEFAULT_CONFIG_FILE, str)
    test_config_file = f"{test_config_name}{s.EXT_YAML}"
    # copy in the config file for this test.
    dir_tests_data: str = f"{s.PKG}.{s.DIR_TESTS_DATA}"
    assert pkg_resources.is_resource(dir_tests_data, test_config_file)
    with open(s.DEFAULT_CONFIG_FILE, "wt") as textfile:
        textfile.write(pkg_resources.read_text(dir_tests_data, test_config_file))
    assert os.path.isfile(s.DEFAULT_CONFIG_FILE)
    # If there is a dir named test_config_name, copy all files in that dir into
    # the temporary testing dir.
    src = pkg_resources.path(dir_tests_data, test_config_name)
    print(type(src))
    # Note: The complex wrapping with Path() seems needed for compatibility down to 3.7.
    if Path(pkg_resources.path(dir_tests_data, test_config_name)).exists():
        if os.path.isdir(Path(pkg_resources.path(dir_tests_data, test_config_name))):
            shutil.copytree(
                pkg_resources.path(dir_tests_data, test_config_name),
                ".",
                dirs_exist_ok=True,
            )
