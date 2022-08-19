"""Test cases for export.py."""
# pylint: disable=redefined-outer-name

import os

import pytest
from click.testing import CliRunner

from tests.helpers import prep_test_config

# from tests.helpers import string_as_config
from yarm.__main__ import cli
from yarm.settings import Settings


@pytest.fixture
def runner() -> CliRunner:
    """Fixture for invoking command-line interfaces."""
    return CliRunner()


def test_export_database(runner: CliRunner) -> None:
    """Database is successfully exported."""
    s = Settings()
    # NOTE We can reuse existing test files for this test.
    test_dir: str = s.DEFAULT_TEST
    with runner.isolated_filesystem():
        prep_test_config(test_dir)
        result = runner.invoke(cli, [s.CMD_RUN, "--database", "-vv"])
        assert result.exit_code == 0
        assert s.MSG_DATABASE_EXPORTED in result.output
        assert os.path.isfile(os.fspath("OUTPUT/BASENAME.db"))


def test_export_tables_csv(runner: CliRunner) -> None:
    """Tables are successfully exported to csv."""
    s = Settings()
    test_dir: str = s.DEFAULT_TEST
    with runner.isolated_filesystem():
        prep_test_config(test_dir)
        result = runner.invoke(cli, [s.CMD_RUN, "-v"])
        assert result.exit_code == 0
        assert s.MSG_TABLES_EXPORTED in result.output
        assert os.path.isfile(os.fspath("OUTPUT/TABLE_FROM_SPREADSHEET.csv"))


def test_export_tables_xlsx(runner: CliRunner) -> None:
    """Tables are successfully exported to xlsx."""
    s = Settings()
    test_dir: str = s.DEFAULT_TEST
    with runner.isolated_filesystem():
        prep_test_config(test_dir, config_file_override="test_export_tables_xlsx.yaml")
        result = runner.invoke(cli, [s.CMD_RUN, "-v"])
        assert result.exit_code == 0
        assert s.MSG_TABLES_EXPORTED in result.output
        assert os.path.isfile(os.fspath(f"OUTPUT/{s.FILE_EXPORT_TABLES_BASENAME}.xlsx"))
