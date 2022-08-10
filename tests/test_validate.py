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


def test_validate_fails_check_is_file(runner: CliRunner) -> None:
    """Validation fails because config file has path to missing file."""
    s = Settings()
    with runner.isolated_filesystem():
        prep_test_config(s.TEST_VALIDATE_FAILS_CHECK_IS_FILE)
        result = runner.invoke(cli, [s.CMD_RUN])
        assert re.search(s.MSG_PATH_NOT_FOUND, result.output)
        assert result.exit_code == 1
