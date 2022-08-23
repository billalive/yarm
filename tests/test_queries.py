"""Test cases for queries.py."""
# pylint: disable=redefined-outer-name

import pytest
from click.testing import CliRunner

from tests.helpers import prep_test_config
from tests.helpers import process_test_tuples

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

    test_config: list = [
        (1, test_dir, s.MSG_QUERY_RUN_ERROR, "query_error.yaml"),
        (
            0,
            test_dir,
            s.MSG_QUERY_REPLACE_COLUMN_ERROR,
            "query_replace_column_error.yaml",
        ),
        (
            1,
            test_dir,
            s.MSG_POSTPROCESS_FUNCTION_NOT_FOUND,
            "postprocess_not_found.yaml",
        ),
        (1, test_dir, s.MSG_POSTPROCESS_WRONG_ARGS, "postprocess_wrong_args_1.yaml"),
        (1, test_dir, s.MSG_POSTPROCESS_WRONG_ARGS, "postprocess_wrong_args_2.yaml"),
        (1, test_dir, s.MSG_POSTPROCESS_OTHER_TYPE_ERROR, "postprocess_key_error.yaml"),
        (1, test_dir, s.MSG_POSTPROCESS_RETURNED_OTHER, "postprocess_return_str.yaml"),
        (
            1,
            test_dir,
            s.MSG_POSTPROCESS_RETURNED_EMPTY_DF,
            "postprocess_return_empty_df.yaml",
        ),
        (0, test_dir, s.MSG_QUERY_EMPTY_ERROR, "query_empty.yaml"),
        (1, test_dir, s.MSG_POSTPROCESS_BUT_NO_IMPORT, "postprocess_no_import.yaml"),
    ]
    process_test_tuples(test_config, runner)

    with runner.isolated_filesystem():
        prep_test_config(
            test_dir, config_file_override="query_replace_match_error.yaml"
        )
        result = runner.invoke(cli, [s.CMD_RUN, "-vvv"])
        assert result.exit_code == 0
        assert s.MSG_QUERY_REPLACE_MATCH_ERROR in result.output
        assert "unterminated character set at" in result.output
        assert "invalid group reference" in result.output
