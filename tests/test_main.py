"""Test cases for the __main__ module."""
# pylint: disable=redefined-outer-name
# pylint: disable=invalid-name
# pylint: disable=import-error


import importlib.resources as pkg_resources
import inspect
import os
import shutil
from typing import Any

import pytest
from click.testing import CliRunner
from path import Path

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
    # Make sure we have a default config file location.
    assert isinstance(s.DEFAULT_CONFIG_FILE, str)
    # Copy in the config file for this test.
    # NOTE Is there a way to avoid hard-coding 'tests_data' here? Does it matter?
    # NOTE We use inspect() rather than importlib() to get this path, because
    # importlib has changed much more since 3.7, esp in how it handles dirs
    # within other dirs. Using inspect() to get the paths seems simpler.
    dir_tests_data: str = os.path.dirname(inspect.getfile(tests_data))
    test_config_file: str = f"{dir_tests_data}/{test_config_name}{s.EXT_YAML}"
    assert os.path.isfile(test_config_file)
    shutil.copy(test_config_file, s.DEFAULT_CONFIG_FILE)
    assert os.path.isfile(s.DEFAULT_CONFIG_FILE)
    # Does this test have a test directory?
    # If so, copy all files from that dir into the temporary testing dir.
    # Use inspect to get the actual path.
    # print("dir_tests_data:", dir_tests_data)
    assert os.path.isdir(os.path.dirname(dir_tests_data))
    dir_test_config_name: str = f"{dir_tests_data}/{test_config_name}"
    # NOTE Next lines tested in: test_prep_config_copies_files()
    if os.path.isdir(os.path.dirname(dir_test_config_name)):  # pragma: no branch
        # print("is a dir:", dir_test_config_name)
        for f in Path(dir_test_config_name).glob("*"):
            if os.path.isfile(f):  # pragma: no branch
                shutil.copy(f, ".")
    # else:
    # print("not a dir:", dir_test_config_name)


def test_prep_config_copies_files(runner: CliRunner) -> None:
    """Copy test_config_name/ files into testing environment."""
    with runner.isolated_filesystem():
        test_config_name: str = "test_prep_config_copies_files"
        prep_test_config(test_config_name)
        assert os.path.isfile("file1.txt")
        assert os.path.isfile("file2.txt")
        assert not os.path.isfile("does_not_exist.txt")
