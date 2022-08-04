"""Functional test cases (user story)."""
import re

import pytest
from click.testing import CliRunner

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
def test_run_new(runner: CliRunner) -> None:
    """It creates a new config file, then opens it in default editor."""
    result = runner.invoke(cli, ["new"])
    assert result.exit_code == 0
    assert re.match("new", result.output)


# She tries to initialize a new project again, but this fails
# because there is already a config file in this directory.


# Then she tries to run the report.
# But she forgot to edit the config file, so she gets a message reminding her
# that she needs to edit the config file first.


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
