"""Test cases for tables.py."""
# pylint: disable=redefined-outer-name

import pytest
from click.testing import CliRunner

from tests.helpers import prep_test_config
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
        assert result.exit_code == 0
