"""Test cases for queries.py."""
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


def test_query_error(runner: CliRunner) -> None:
    """Query error triggers correct message."""
    s = Settings()
    test_dir: str = "test_queries_options"
    with runner.isolated_filesystem():
        prep_test_config(test_dir)
        result = runner.invoke(cli, [s.CMD_RUN, "-vvv"])
        assert result.exit_code == 0
    with runner.isolated_filesystem():
        prep_test_config(test_dir, config_file_override="query_error.yaml")
        result = runner.invoke(cli, [s.CMD_RUN, "-vvv"])
        assert result.exit_code == 1
        assert s.MSG_QUERY_RUN_ERROR in result.output
    with runner.isolated_filesystem():
        prep_test_config(
            test_dir, config_file_override="query_replace_column_error.yaml"
        )
        result = runner.invoke(cli, [s.CMD_RUN, "-vvv"])
        assert result.exit_code == 0
        assert s.MSG_QUERY_REPLACE_COLUMN_ERROR in result.output
    with runner.isolated_filesystem():
        prep_test_config(
            test_dir, config_file_override="query_replace_match_error.yaml"
        )
        result = runner.invoke(cli, [s.CMD_RUN, "-vvv"])
        assert result.exit_code == 0
        assert s.MSG_QUERY_REPLACE_MATCH_ERROR in result.output
        assert "unterminated character set at" in result.output
        assert "invalid group reference" in result.output
