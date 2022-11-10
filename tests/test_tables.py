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
    test_dir: str = "test_create_tables"
    with runner.isolated_filesystem():
        prep_test_config(test_dir)
        result = runner.invoke(cli, [s.CMD_RUN, "-vv"])
        assert result.exit_code == 0
        assert s.MSG_CREATING_TABLE in result.output
        assert s.MSG_CREATED_TABLE in result.output


def test_df_input_options(runner: CliRunner) -> None:
    """Options in input: are successfully applied."""
    s = Settings()
    test_dir: str = "test_df_input_options"
    append_config: str = ""
    with runner.isolated_filesystem():
        prep_test_config(test_dir)
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
        prep_test_config(test_dir, append_config=append_config)
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
        prep_test_config(test_dir, append_config=append_config)
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
        prep_test_config(test_dir, append_config=append_config)
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
        prep_test_config(test_dir, append_config=append_config)
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
    test_dir: str = "test_df_tables_config_options"
    append_config: str = ""
    with runner.isolated_filesystem():
        prep_test_config(test_dir)
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
        prep_test_config(test_dir, append_config=append_config)
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
        prep_test_config(test_dir, append_config=append_config)
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
        prep_test_config(test_dir, append_config=append_config)
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
        prep_test_config(test_dir, append_config=append_config)
        result = runner.invoke(cli, [s.CMD_RUN, "-vvv"])
        assert result.exit_code == 1
        assert s.MSG_MISSING_DATETIME in result.output
    with runner.isolated_filesystem():
        append_config = """
  products2:
    - path: products.badext
"""
        prep_test_config(test_dir, append_config=append_config)
        result = runner.invoke(cli, [s.CMD_RUN, "-vvv"])
        assert result.exit_code == 1
        assert s.MSG_BAD_FILE_EXT in result.output
    with runner.isolated_filesystem():
        append_config = """
    - path: products_pivot2.csv
"""
        prep_test_config(test_dir, append_config=append_config)
        result = runner.invoke(cli, [s.CMD_RUN, "-vvv"])
        assert result.exit_code == 0
        # Successful merge.
        assert "products_pivot2.csv" in result.output
    with runner.isolated_filesystem():
        append_config = """
    - path: products_merge_missing_cols.csv
"""
        prep_test_config(test_dir, append_config=append_config)
        result = runner.invoke(cli, [s.CMD_RUN, "-vvv"])
        assert result.exit_code == 0
    #     with runner.isolated_filesystem():
    #         append_config = """
    #     - path: products_merge_value_error.csv
    # """
    #         prep_test_config(test_dir, append_config=append_config)
    #         result = runner.invoke(cli, [s.CMD_RUN, "-vvv"])
    #         print("RESULT OUTPUT:")
    #         print(result.output)
    #         assert result.exit_code == 1
    #         assert s.MSG_CREATE_TABLE_VALUE_ERROR in result.output
    with runner.isolated_filesystem():
        append_config = """
input:
  include_index: true
"""
        prep_test_config(test_dir, append_config=append_config)
        result = runner.invoke(cli, [s.CMD_RUN, "-vvv"])
        assert result.exit_code == 0
        assert s.MSG_INCLUDE_INDEX_ALL_TRUE in result.output
    with runner.isolated_filesystem():
        append_config = """
input:
  include_index: false
"""
        prep_test_config(test_dir, append_config=append_config)
        result = runner.invoke(cli, [s.CMD_RUN, "-vvv"])
        assert result.exit_code == 0
        assert s.MSG_INCLUDE_INDEX_ALL_FALSE in result.output
    with runner.isolated_filesystem():
        append_config = """
      include_index: true
    - path: products_pivot2.csv
      include_index: true
"""
        prep_test_config(test_dir, append_config=append_config)
        result = runner.invoke(cli, [s.CMD_RUN, "-vvv"])
        assert result.exit_code == 1
        assert s.MSG_INCLUDE_INDEX_TABLE_CONFLICT in result.output
    with runner.isolated_filesystem():
        prep_test_config(test_dir)
        # Write a file where output_dir should be.
        with open("output", "w") as f:
            f.write("")
        result = runner.invoke(cli, [s.CMD_RUN, "-vvv"])
        assert s.MSG_CANT_CREATE_OUTPUT_DIR in result.output
        assert result.exit_code == 1
    # Break tables_config with input: options.
    # First run should pass.
    with runner.isolated_filesystem():
        prep_test_config(test_dir, config_file_override="slugify_error.yaml")
        result = runner.invoke(cli, [s.CMD_RUN, "-vvv"])
        assert result.exit_code == 0
        assert s.MSG_APPLYING_PIVOT in result.output
        assert s.MSG_CONVERTING_DATETIME in result.output
    # Then we apply input options without updating tables_config,
    # and things break.
    with runner.isolated_filesystem():
        append_config = """
tables_config:
  dates:
    - path: slugify_error_datetime.csv
      datetime:
        "DATE CREATED":

input:
  slugify_columns: true
"""
        prep_test_config(
            test_dir, config_file_override="minimum.yaml", append_config=append_config
        )
        result = runner.invoke(cli, [s.CMD_RUN, "-vvv"])
        print(result.output)
        assert s.MSG_MISSING_DATETIME in result.output
        assert result.exit_code == 1
    with runner.isolated_filesystem():
        append_config = """
tables_config:
  pivoting:
    - path: slugify_error_pivot.csv
      pivot:
        index: ID
        columns: KEY
        values: "VALUE NAME"

input:
  slugify_columns: true
"""
        prep_test_config(
            test_dir, config_file_override="minimum.yaml", append_config=append_config
        )
        result = runner.invoke(cli, [s.CMD_RUN, "-vvv"])
        print(result.output)
        assert s.MSG_PIVOT_FAILED_KEY_ERROR in result.output
        assert result.exit_code == 1
    with runner.isolated_filesystem():
        append_config = """
tables_config:
  dates:
    - path: slugify_error_datetime.csv
      datetime:
        "DATE CREATED":

input:
  lowercase_columns: true
"""
        prep_test_config(
            test_dir, config_file_override="minimum.yaml", append_config=append_config
        )
        result = runner.invoke(cli, [s.CMD_RUN, "-vvv"])
        print(result.output)
        assert s.MSG_MISSING_DATETIME in result.output
        assert result.exit_code == 1
    with runner.isolated_filesystem():
        append_config = """
tables_config:
  pivoting:
    - path: slugify_error_pivot.csv
      pivot:
        index: ID
        columns: KEY
        values: "VALUE NAME"

input:
  lowercase_columns: true
"""
        prep_test_config(
            test_dir, config_file_override="minimum.yaml", append_config=append_config
        )
        result = runner.invoke(cli, [s.CMD_RUN, "-vvv"])
        print(result.output)
        assert s.MSG_PIVOT_FAILED_KEY_ERROR in result.output
        assert result.exit_code == 1


def test_df_empty(runner: CliRunner) -> None:
    """Empty df triggers correct message."""
    s = Settings()
    test_dir: str = "test_df_empty"
    with runner.isolated_filesystem():
        prep_test_config(test_dir)
        result = runner.invoke(cli, [s.CMD_RUN, "-vvv"])
        assert s.MSG_EMPTY_DF in result.output
        assert s.MSG_EMPTY_DF_ORIGINAL in result.output
        # Warning, not error.
        assert result.exit_code == 0
