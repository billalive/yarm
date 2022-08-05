"""Test cases for the __main__ module."""
import importlib.resources as pkg_resources

import pytest
from click.testing import CliRunner

from yarm import __main__

# from yarm.__main__ import cli
from yarm.__main__ import default_config_file
from yarm.__main__ import dir_templates


# import os


@pytest.fixture
def runner() -> CliRunner:
    """Fixture for invoking command-line interfaces."""
    return CliRunner()


def test_main_succeeds(runner: CliRunner) -> None:
    """It exits with a status code of zero."""
    result = runner.invoke(__main__.cli)
    assert result.exit_code == 0


def test_default_config_template_exists() -> None:
    """The default config file template exists."""
    # assert pkg_resources.is_resource("yarm", template_config_name)
    assert pkg_resources.is_resource(f"yarm.{dir_templates}", default_config_file)


# def test_importlib_works_in_isolated_filesystem(runner: CliRunner) -> None:
#     """importlib.resource can find a template within a click isolated filesystem.

#     This test was used to figure out why pkg_resources.path was erroring out
#     on Python versions <= 3.9. The solution was to use pkg_resources.read_text(),
#     which works correctly on older versions.
#     """
#     assert pkg_resources.is_resource(f"yarm.{dir_templates}", default_config_file)
#     print(
#         "path outside isolated filesystem:",
#         pkg_resources.path(f"yarm.{dir_templates}", default_config_file),
#     )
#     print(
#         "template:",
#         pkg_resources.read_text(f"yarm.{dir_templates}", default_config_file),
#     )
#     with runner.isolated_filesystem():
#         assert pkg_resources.is_resource(f"yarm.{dir_templates}", default_config_file)
#         path_template_config_file: str = str(
#             pkg_resources.path(f"yarm.{dir_templates}", default_config_file)
#         )
#         print("temporary filesystem", os.getcwd())
#         print("path to template (inside):", str(path_template_config_file))
#    To see these print statements, the test needs to fail.
#    assert False
