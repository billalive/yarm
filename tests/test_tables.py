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
        assert s.MSG_CREATING_TABLE in result.output
        assert s.MSG_CREATED_TABLE in result.output
        assert result.exit_code == 0


def test_df_input_options(runner: CliRunner) -> None:
    """Options in input: are successfully applied."""
    s = Settings()
    test_config_name: str = "test_df_input_options"
    append_config: str = ""
    with runner.isolated_filesystem():
        prep_test_config(test_config_name)
        result = runner.invoke(cli, [s.CMD_RUN, "-vvv"])
        assert "Venkman " in result.output
        assert "First Name" in result.output
        assert s.MSG_NO_SHEET_PROVIDED in result.output
        assert result.exit_code == 0
    with runner.isolated_filesystem():
        append_config = """
input:
  strip: true
"""
        prep_test_config(test_config_name, append_config=append_config)
        result = runner.invoke(cli, [s.CMD_RUN, "-vvv"])
        assert "Venkman " not in result.output
        assert "Venkman" in result.output
        assert result.exit_code == 0
    with runner.isolated_filesystem():
        append_config = """
input:
  lowercase_columns: true
"""
        prep_test_config(test_config_name, append_config=append_config)
        result = runner.invoke(cli, [s.CMD_RUN, "-vvv"])
        assert "First Name" not in result.output
        assert "first_name" not in result.output
        assert "first name" in result.output
        assert result.exit_code == 0
    with runner.isolated_filesystem():
        append_config = """
input:
  slugify_columns: true
  lowercase_columns: true
"""
        prep_test_config(test_config_name, append_config=append_config)
        result = runner.invoke(cli, [s.CMD_RUN, "-vvv"])
        assert "First Name" not in result.output
        assert "First_Name" not in result.output
        assert "first name" not in result.output
        assert "first_name" in result.output
        assert result.exit_code == 0
    with runner.isolated_filesystem():
        append_config = """
input:
  uppercase_rows: true
"""
        prep_test_config(test_config_name, append_config=append_config)
        result = runner.invoke(cli, [s.CMD_RUN, "-vvv"])
        assert "    Peter" not in result.output
        assert "Peter" not in result.output
        assert "PETER" in result.output
        assert result.exit_code == 0
