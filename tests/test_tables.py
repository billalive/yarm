"""Test cases for tables.py."""
# pylint: disable=redefined-outer-name

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


def test_create_tables(runner: CliRunner) -> None:
    """Tables are successfully created."""
    s = Settings()
    test_config_name: str = "test_create_tables"
    with runner.isolated_filesystem():
        prep_test_config(test_config_name)
        result = runner.invoke(cli, [s.CMD_RUN, "-vv"])
        assert result.exit_code == 0
        assert s.MSG_CREATING_TABLE in result.output
        assert s.MSG_CREATED_TABLE in result.output


def test_df_input_options(runner: CliRunner) -> None:
    """Options in input: are successfully applied."""
    s = Settings()
    test_config_name: str = "test_df_input_options"
    append_config: str = ""
    with runner.isolated_filesystem():
        prep_test_config(test_config_name)
        result = runner.invoke(cli, [s.CMD_RUN, "-vvv"])
        assert result.exit_code == 0
        assert "Venkman " in result.output
        assert "First Name" in result.output
        assert s.MSG_NO_SHEET_PROVIDED in result.output
    with runner.isolated_filesystem():
        append_config = """
input:
  strip: true
"""
        prep_test_config(test_config_name, append_config=append_config)
        result = runner.invoke(cli, [s.CMD_RUN, "-vvv"])
        assert result.exit_code == 0
        assert "Venkman " not in result.output
        assert "Venkman" in result.output
        assert s.MSG_STRIP_WHITESPACE in result.output
        assert s.MSG_SLUGIFY_COLUMNS not in result.output
        assert s.MSG_LOWERCASE_COLUMNS not in result.output
        assert s.MSG_UPPERCASE_ROWS not in result.output
    with runner.isolated_filesystem():
        append_config = """
input:
  lowercase_columns: true
"""
        prep_test_config(test_config_name, append_config=append_config)
        result = runner.invoke(cli, [s.CMD_RUN, "-vvv"])
        assert result.exit_code == 0
        assert "First Name" not in result.output
        assert "first_name" not in result.output
        assert "first name" in result.output
        assert s.MSG_STRIP_WHITESPACE not in result.output
        assert s.MSG_SLUGIFY_COLUMNS not in result.output
        assert s.MSG_LOWERCASE_COLUMNS in result.output
        assert s.MSG_UPPERCASE_ROWS not in result.output
    with runner.isolated_filesystem():
        append_config = """
input:
  slugify_columns: true
  lowercase_columns: true
"""
        prep_test_config(test_config_name, append_config=append_config)
        result = runner.invoke(cli, [s.CMD_RUN, "-vvv"])
        assert result.exit_code == 0
        assert "First Name" not in result.output
        assert "First_Name" not in result.output
        assert "first name" not in result.output
        assert "first_name" in result.output
        assert s.MSG_STRIP_WHITESPACE not in result.output
        assert s.MSG_SLUGIFY_COLUMNS in result.output
        assert s.MSG_LOWERCASE_COLUMNS in result.output
        assert s.MSG_UPPERCASE_ROWS not in result.output
    with runner.isolated_filesystem():
        append_config = """
input:
  uppercase_rows: true
"""
        prep_test_config(test_config_name, append_config=append_config)
        result = runner.invoke(cli, [s.CMD_RUN, "-vvv"])
        assert result.exit_code == 0
        assert "    Peter" not in result.output
        assert "Peter" not in result.output
        assert "PETER" in result.output
        assert s.MSG_STRIP_WHITESPACE not in result.output
        assert s.MSG_SLUGIFY_COLUMNS not in result.output
        assert s.MSG_LOWERCASE_COLUMNS not in result.output
        assert s.MSG_UPPERCASE_ROWS in result.output


def test_df_tables_config_options(runner: CliRunner) -> None:
    """Table options in tables_config: are successfully applied."""
    s = Settings()
    test_config_name: str = "test_df_tables_config_options"
    append_config: str = ""
    with runner.isolated_filesystem():
        prep_test_config(test_config_name)
        result = runner.invoke(cli, [s.CMD_RUN, "-vvv"])
        assert result.exit_code == 0
        assert s.MSG_APPLYING_PIVOT not in result.output
        assert s.MSG_CONVERTING_DATETIME not in result.output
    with runner.isolated_filesystem():
        append_config = """
      pivot:
        index: id
        columns: key
        values: value
"""
        prep_test_config(test_config_name, append_config=append_config)
        result = runner.invoke(cli, [s.CMD_RUN, "-vvv"])
        assert result.exit_code == 0
        assert s.MSG_APPLYING_PIVOT in result.output
        assert s.MSG_CONVERTING_DATETIME not in result.output
        assert "key discount                          name" in result.output
    with runner.isolated_filesystem():
        append_config = """
      pivot:
        index: id_missing
        columns: key
        values: value
"""
        prep_test_config(test_config_name, append_config=append_config)
        result = runner.invoke(cli, [s.CMD_RUN, "-vvv"])
        assert result.exit_code == 1
        assert s.MSG_PIVOT_FAILED_KEY_ERROR in result.output
    with runner.isolated_filesystem():
        append_config = """
  orders:
    - path: orders.xlsx
      sheet: Orders
      datetime:
        ordered:
        shipped: "%b, %d, %Y"
"""
        prep_test_config(test_config_name, append_config=append_config)
        result = runner.invoke(cli, [s.CMD_RUN, "-vvv"])
        assert result.exit_code == 0
        assert s.MSG_APPLYING_PIVOT not in result.output
        assert s.MSG_CONVERTING_DATETIME in result.output
        assert "2004-10-01" in result.output
        assert "Oct, 15, 2004" in result.output
    with runner.isolated_filesystem():
        append_config = """
  orders:
    - path: orders.xlsx
      sheet: Orders
      datetime:
        missing:
"""
        prep_test_config(test_config_name, append_config=append_config)
        result = runner.invoke(cli, [s.CMD_RUN, "-vvv"])
        assert result.exit_code == 1
        assert s.MSG_MISSING_DATETIME in result.output

    # TODO Test creating different tables, with different options, from the same path
    # - path 1: pivot columns into new renamed columns.
    # - path 2: data starts out with those renamed columns.

    # TODO test merging paths with same columns
    # TODO test merging paths when a later path adds columns
    # TODO test merging paths when a later path has fewer columns
    # TODO test merging paths when field with same name doesn't match: ValueError
    # TODO test merging paths when no columns in common: MergeError
    # TODO test columns have different case, but you lowercase all, should work
