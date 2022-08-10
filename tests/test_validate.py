#!/usr/bin/env python3
"""Test cases for the __validate__ module."""
# pylint: disable=redefined-outer-name
# pylint: disable=invalid-name
# pylint: disable=import-error


import re

import pytest
from click.testing import CliRunner

from tests.test_main import prep_test_config
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
    ]
    for test_tuple in test_config:
        exit_code: int = test_tuple[0]
        test: str = test_tuple[1]
        msg: str = test_tuple[2]
        print("test:", test, "msg:", msg)
        with runner.isolated_filesystem():
            prep_test_config(test)
            result = runner.invoke(cli, [s.CMD_RUN])
            assert re.search(msg, result.output)
            assert result.exit_code == exit_code
