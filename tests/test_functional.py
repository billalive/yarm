"""Functional test cases (user story)."""
import os
import re

import pytest
from click.testing import CliRunner

from yarm.__main__ import Settings
from yarm.__main__ import cli


@pytest.fixture
def runner() -> CliRunner:
    """Fixture for invoking command-line interfaces."""
    return CliRunner()


# Alicia wants to try this new tool.
# She tries running yarm with no arguments to see what happens.
def test_no_arguments_show_welcome(runner: CliRunner) -> None:
    """With no arguments, it shows a welcome message."""
    result = runner.invoke(cli)
    assert result.exit_code == 0
    assert re.match("yarm: Yet Another Report Maker.", result.output)


# She gets a warning that she needs to either supply a
# configuration file or initialize a new project.
# She tries the help.
def test_show_help(runner: CliRunner) -> None:
    """It shows the help screen."""
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert re.match("Usage:", result.output)


# She decides to initialize a new project.

# INITIALIZE A NEW PROJECT

# She initializes a new project.
# Since she dislikes automatic editors, she passes "--no-edit"
def test_new_create_config_no_edit(runner: CliRunner) -> None:
    """It creates a new config file (but skips click.edit).

    Note: the default behavior is to open the config file with click.edit(),
    but there is currently no simple way to test click.edit().
    https://github.com/pallets/click/issues/1720
    """
    s = Settings()
    # Test in a temporary new directory.
    with runner.isolated_filesystem():
        assert isinstance(s.DEFAULT_CONFIG_FILE, str)
        result = runner.invoke(cli, ["new", "--no-edit"])
        assert os.path.isfile(s.DEFAULT_CONFIG_FILE)
        assert result.exit_code == 0


# She tries to initialize a new project again, but this fails
# because there is already a config file in this directory.
def test_new_config_file_exists_abort(runner: CliRunner) -> None:
    """It detects an existing config file and aborts."""
    s = Settings()
    with runner.isolated_filesystem():
        assert isinstance(s.DEFAULT_CONFIG_FILE, str)
        # Run once, to generate the first config file.
        result = runner.invoke(cli, ["new", "--no-edit"])
        # Run a second time.
        result = runner.invoke(cli, ["new", "--no-edit"])
        assert re.match(s.MSG_ABORT, result.output)
        assert result.exit_code == 1


# Irritated, she forces yarm to overwrite this existing config file.
def test_new_config_file_exists_force(runner: CliRunner) -> None:
    """It detects an existing config file, but forces an overwrite."""
    s = Settings()
    with runner.isolated_filesystem():
        assert isinstance(s.DEFAULT_CONFIG_FILE, str)
        # Run once, to generate the first config file.
        result = runner.invoke(cli, ["new", "--no-edit"])
        # Run a second time, and force overwrite.
        result = runner.invoke(cli, ["new", "--no-edit", "--force"])
        assert re.match(s.MSG_WARN, result.output)
        assert os.path.isfile(s.DEFAULT_CONFIG_FILE)
        assert result.exit_code == 0


# Then she decides to initalize a new project using a custom name for
# the config file.
def test_new_config_file_custom(runner: CliRunner) -> None:
    """It creates a config file with a custom name."""
    s = Settings()
    with runner.isolated_filesystem():
        assert isinstance(s.TEST_CUSTOM_CONFIG_FILE, str)
        result = runner.invoke(
            cli, ["new", "--no-edit", "--path", s.TEST_CUSTOM_CONFIG_FILE]
        )
        assert re.match(s.MSG_SUCCESS, result.output)
        assert os.path.isfile(s.TEST_CUSTOM_CONFIG_FILE)
        assert result.exit_code == 0


# Just for good measure, she tries to initialize a new project again,
# using that same custom name. This fails, because that file exists.
def test_new_config_file_custom_exists_abort(runner: CliRunner) -> None:
    """It detects an existing custom config file and aborts."""
    s = Settings()
    with runner.isolated_filesystem():
        assert isinstance(s.DEFAULT_CONFIG_FILE, str)
        # Run once, to generate the first config file.
        result = runner.invoke(
            cli, ["new", "--no-edit", "--path", s.TEST_CUSTOM_CONFIG_FILE]
        )
        # Run a second time.
        result = runner.invoke(
            cli, ["new", "--no-edit", "--path", s.TEST_CUSTOM_CONFIG_FILE]
        )
        assert re.match(s.MSG_ABORT, result.output)
        assert result.exit_code == 1


# Now even more irritated, she overwrites that custom file with --force
def test_new_config_file_custom_exists_force(runner: CliRunner) -> None:
    """It detects an existing custom config file and aborts."""
    s = Settings()
    with runner.isolated_filesystem():
        assert isinstance(s.DEFAULT_CONFIG_FILE, str)
        # Run once, to generate the first config file.
        result = runner.invoke(
            cli, ["new", "--no-edit", "--path", s.TEST_CUSTOM_CONFIG_FILE]
        )
        # Run a second time, with --force.
        result = runner.invoke(
            cli, ["new", "--no-edit", "--force", "--path", s.TEST_CUSTOM_CONFIG_FILE]
        )
        assert re.match(s.MSG_WARN, result.output)
        assert os.path.isfile(s.TEST_CUSTOM_CONFIG_FILE)
        assert result.exit_code == 0


# Satisfied, she decides that maybe the default config file is fine after all.
# Then she tries to run the report.
# But she forgot to edit the config file, so she gets a message reminding
# her that she needs to edit the config file first.


def test_report_aborts_invalid_config_no_edits(runner: CliRunner) -> None:
    """Report aborts because config file not edited."""
    s = Settings()
    with runner.isolated_filesystem():
        assert isinstance(s.DEFAULT_CONFIG_FILE, str)
        # Generate default config file.
        result = runner.invoke(cli, ["new", "--no-edit"])
        # Try to run report.
        result = runner.invoke(cli)
        assert os.path.isfile(s.DEFAULT_CONFIG_FILE)
        assert re.match(s.MSG_ABORT, result.output)
        assert result.exit_code == 1


# TODO Tokenize template file and get words with all caps from it.
# Be careful that all words are implausible enough that they wouldn't appear
# in an actual spreadsheet.


# She cleverly edits only the config line that's preventing the report from
# running and tries again.
# But now the report fails because the data files don't exist.


# EXPORT TABLES

# She edits the config to point to one actual data file, a CSV.
# But she has not specified any output.
# The message explains that for the report to run, she must specify
# one or more of:
# - export_tables: csv
# - at least one entry under queries:


# She tries setting export_tables to csv.


# Unfortunately, and most unluckily, she already happens to have a subdir with
# the same default name for the output directory. It has important,
# irreplaceable files, not under version control, that could be
# clobbered by the tool!
#
# Fortunately, the tool detects this and asks for confirmation before
# proceeding.
#
# At first, she says 'no'.
#
# So the tool aborts.
#
# Then she realizes she doesn't care about those files anyway.
# She tries running the command again.
#
# And when the tool asks again, this time she says 'yes'.
#
# The tool overwrites the file.
#
# Success! The tool has imported a single CSV, and output a modified CSV.
#
# Alicia makes a mental note to explore these options more fully later.
# For now, she wants to make sure this tool can import more than one data
# source.
#
# Excited, Alicia adds another source, this time a spreadsheet.
# She tries running the report.
#
# But she forgot to specify which sheet she wanted for the spreadsheet,
# so the report aborts.
#
# Irritated, Alicia specifies the sheet in the config file.
#
# She reruns the report.
#
# Again the tool detects that there are already files in the output directory.
#
# Again it asks for confirmation before proceeding.
#
# Even more irritated, Alicia wonders whether she will need to confirm this
# every time. Then she remembers that she can add an argument to force
# the overwrite. She reruns the tool with this argument.
#
# Success! Now both data sources have been exported to CSVs in the output dir.
#

# QUERIES

# Alicia decides to query these tables she's created.
# She adds a simple SELECT * from one of the tables.
#
# Then runs the report.
#
# Success! The output CSV shows all the columns.
#
# Then she adds a more complex query that uses both tables.
#
# She runs the report.
#
# Success! The output CSV shows all the columns from both tables.
#
# TODO Write tests for more query options.


# TABLE OPTIONS

# Because the default config file has "slugify-columns" set as True...
#
# ... we can confirm that while the original CSV had an ugly column name
# with spaces and punctuation...
#
# ... the new file has a lovely column name that is easy to work with.

# TODO Write a test for every config option.
