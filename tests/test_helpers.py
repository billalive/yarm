"""Test cases for helpers.py."""
# pylint: disable=redefined-outer-name

import pytest
from click.testing import CliRunner

from tests.helpers import string_as_config
from yarm.__main__ import cli
from yarm.settings import Settings


@pytest.fixture
def runner() -> CliRunner:
    """Fixture for invoking command-line interfaces."""
    return CliRunner()


def test_load_yaml_file_scanner_error(runner: CliRunner) -> None:
    """load_yaml_file fails.

    See https://github.com/crdoconnor/strictyaml/issues/22

    """
    s = Settings()
    with runner.isolated_filesystem():
        string_as_config(
            """
        queries:
            - name: name with: colon ... oops
"""
        )
        result = runner.invoke(cli, [s.CMD_RUN])
        # FIXME typeguard sometimes trips a scanner error, but I'm not sure how.
        # Find a config fragment that will trigger ScannerError
        # assert s.MSG_INVALID_YAML_SCANNER in result.output
        assert s.MSG_INVALID_YAML in result.output
