#!/usr/bin/env python3
"""Test cases for the __validate__ module."""
# pylint: disable=redefined-outer-name
# pylint: disable=invalid-name
# pylint: disable=import-error

import pytest
from click.testing import CliRunner

from tests.test_helpers import assert_files_exist
from tests.test_helpers import assert_messages
from tests.test_helpers import prep_test_config
from tests.test_helpers import string_as_config
from yarm.__main__ import cli
from yarm.settings import Settings


@pytest.fixture
def runner() -> CliRunner:
    """Fixture for invoking command-line interfaces."""
    return CliRunner()


def test_validate_config_mistakes(runner: CliRunner) -> None:
    """Validation fails on a series of config mistakes."""
    s = Settings()
    # Each mistake is defined in a short test file, and the result
    # should be a particular message or messages.
    test_config: list = [
        (1, "test_validate_fails_check_is_file", s.MSG_VALIDATING_KEY),
        (1, "test_validate_fails_check_is_file", s.MSG_PATH_NOT_FOUND),
        (0, "test_validate_tables_config_valid_mwe", s.MSG_CONFIG_FILE_VALID),
        (1, "test_validate_missing_required_key", s.MSG_MISSING_REQUIRED_KEY),
        (
            1,
            "test_validate_need_export_tables_or_queries",
            s.MSG_NEED_EXPORT_TABLES_OR_QUERIES,
        ),
        (0, "test_validate_export_tables_only", s.MSG_EXPORT_TABLES_ONLY),
    ]
    for test_tuple in test_config:
        exit_code: int = test_tuple[0]
        test: str = test_tuple[1]
        msg: str = test_tuple[2]
        print("test:", test, "msg:", msg)
        with runner.isolated_filesystem():
            prep_test_config(test)
            result = runner.invoke(cli, [s.CMD_RUN])
            assert result.output.find(msg)
            assert result.exit_code == exit_code


def test_validate_complete_config_valid(runner: CliRunner) -> None:
    """Validation succeeds with values for every config option.

    If you modify, add or remove a config option:

    - Update this test and its config file.
    - Update validate_config_schema()
    - Update templates/yarm.yaml if this key appears there.
    """
    s = Settings()
    test: str = "test_validate_complete_config_valid"
    files: list = [
        "MODULE_A.py",
        "SOURCE_A.xlsx",
        "SOURCE_B.csv",
        "SOURCE_C.xlsx",
        "SOURCE_D.csv",
    ]
    # TODO Should this list of keys to check for be dynamically
    # generated? Or is hard-coding it (again) the point of a test?
    # TODO Uncoment include and create_tables when we implement these options.
    messages: list = [
        s.MSG_CONFIG_FILE_VALID,
        s.MSG_VALIDATING_KEY,
        f"{s.MSG_VALIDATING_KEY}: tables_config",
        f"{s.MSG_VALIDATING_KEY} table: table_from_spreadsheet",
        f"{s.MSG_VALIDATING_KEY} table: table_from_csv",
        f"{s.MSG_VALIDATING_KEY} table: table_from_multiple_sources",
        f"{s.MSG_VALIDATING_KEY}: import",
        f"{s.MSG_VALIDATING_KEY}: input",
        f"{s.MSG_VALIDATING_KEY}: output",
        f"{s.MSG_VALIDATING_KEY}: queries",
    ]
    with runner.isolated_filesystem():
        prep_test_config(test)
        result = runner.invoke(cli, [s.CMD_RUN, "-vv"])
        assert_files_exist(files)
        assert_messages(messages, result.output)
        assert result.exit_code == 0


def test_validate_invalid_config(runner: CliRunner) -> None:
    """Invalid config fragments that should fail."""
    s = Settings()
    fragments = [
        (
            """
bad_key_top:
""",
            s.MSG_TEST_KEY_NOT_IN_SCHEMA,
        ),
        (
            """
import:
  - path:
""",
            "path",
        ),
        (
            """
import:
  - bad_key:
""",
            s.MSG_TEST_KEY_NOT_IN_SCHEMA,
        ),
        (
            """
output:
  bad_key:
""",
            s.MSG_TEST_KEY_NOT_IN_SCHEMA,
        ),
        (
            """
output:
  basename: BASENAME
  styles:
    column_width: fifteen
""",
            "found arbitrary text",
        ),
        # Each table needs to be a list.
        (
            """
tables_config:
  table_from_spreadsheet:
    path: SOURCE_A.xlsx
    sheet: SHEET A.1
""",
            s.MSG_TEST_EXPECTED_LIST,
        ),
        (
            """
queries:
  name:
  sql:
""",
            s.MSG_TEST_EXPECTED_LIST,
        ),
    ]
    for fragment in fragments:
        fragment_config = fragment[0]
        fragment_msg = fragment[1]
        messages: list = [
            s.MSG_INVALID_YAML,
            fragment_msg,
        ]
        with runner.isolated_filesystem():
            string_as_config(fragment_config)
            result = runner.invoke(cli, [s.CMD_RUN])
            assert_messages(messages, result.output)
            assert result.exit_code == 1
