"""Test cases for helpers.py."""
# pylint: disable=redefined-outer-name

import os
from typing import Any
from unittest import mock

import pytest
from click.testing import CliRunner

from tests.helpers import prep_test_config
from tests.helpers import string_as_config
from yarm.__main__ import cli
from yarm.settings import Settings


@pytest.fixture
def runner() -> CliRunner:
    """Fixture for invoking command-line interfaces."""
    return CliRunner()


def test_load_yaml_file_scanner_error(runner: CliRunner) -> None:
    """load_yaml_file fails.

    See https://github.com/crdoconnor/strictyaml/issues/22

    """
    s = Settings()
    with runner.isolated_filesystem():
        string_as_config(
            """
        queries:
            - name: name with: colon ... oops
"""
        )
        result = runner.invoke(cli, [s.CMD_RUN])
        # FIXME typeguard sometimes trips a scanner error, but I'm not sure how.
        # Find a config fragment that will trigger ScannerError
        # assert s.MSG_INVALID_YAML_SCANNER in result.output
        assert s.MSG_INVALID_YAML in result.output


@pytest.fixture
def mock_click_confirm(monkeypatch: Any) -> Any:
    """When 'testing' click.confirm(), return True.

    TODO Also test False answers.
    """

    def fake_click_confirm(
        *args: Any, **kwargs: Any  # pylint: disable=unused-argument  # pragma: no cover
    ) -> Any:
        return True  # pragma: no cover

    monkeypatch.setattr("click.confirm", fake_click_confirm)  # pragma: no cover


@mock.patch("click.confirm")
def test_overwrite_file(mock_click, runner: CliRunner) -> None:
    """overwrite_file() works as expected."""
    s = Settings()
    test_dir: str = "test_overwrite_file"
    file_test: str = "output/products.csv"

    with runner.isolated_filesystem():
        prep_test_config(test_dir)
        result = runner.invoke(cli, [s.CMD_RUN, "-vvv"])
        print(result.output)
        assert result.exit_code == 0
        assert s.MSG_REMOVED_FILE not in result.output
    with runner.isolated_filesystem():
        prep_test_config(test_dir)
        os.makedirs("output")
        with open(file_test, "w") as f:
            f.write("test")
        result = runner.invoke(cli, [s.CMD_RUN, "-vvv"])
        print(result.output)
        assert result.exit_code == 0
        assert s.MSG_REMOVED_FILE in result.output
        assert s.MSG_REMOVED_FILE_FORCE not in result.output
    with runner.isolated_filesystem():
        prep_test_config(test_dir)
        os.makedirs("output")
        with open(file_test, "w") as f:
            f.write("test")
        result = runner.invoke(cli, [s.CMD_RUN, "-vvv", "--force"])
        print(result.output)
        assert result.exit_code == 0
        assert s.MSG_REMOVED_FILE not in result.output
        assert s.MSG_REMOVED_FILE_FORCE in result.output
