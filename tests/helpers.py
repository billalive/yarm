"""Helper functions for tests."""
import inspect
import os
import shutil
import sys
from typing import List

from path import Path

from yarm import tests_data
from yarm.__main__ import cli
from yarm.settings import Settings


def assert_files_exist(files: List[str]) -> bool:
    """Assert that each file in files exists."""
    for f in files:
        assert os.path.isfile(f)
    return True


def assert_messages(messages: List[str], output: str) -> bool:
    """Assert that each message in messages appears in output."""
    for msg in messages:
        assert msg in output
    return True


def prep_test_config(
    test_dir: str,
    append_config: str = "",
    config_file_override: str = "",
    print_config: bool = False,
) -> None:
    """Prepare test config file for a particular test.

    Several tests need a particular file in place as the config file
    for the test. This helper function sets that up.

    Use this helper function inside other tests.

    To prepare a new test:

    - Create test_dir as directory in tests_data/.
      Every file in this dir will be copied into the temporary dir for this test.

    - In this directory, create a config file with name defined in s.DEFAULT_CONFIG_FILE

    - If needed, add any supporting files.

    Args:
        test_dir (str): directory with files for this test.
        config_file_override (str): (optional) use this config file
            File path must be relative to directory of test_dir.
        append_config (str): (optional) append this string as config
        print_config (bool): (optional) print the config file

    """
    s = Settings()

    # NOTE Is there a way to avoid hard-coding 'tests_data' here? Does it matter?
    # NOTE We use inspect() rather than importlib() to get this path, because
    # importlib has changed much more since 3.7, esp in how it handles dirs
    # within other dirs. Using inspect() to get the paths seems simpler.
    # TODO Since pandas requires 3.8, would 3.8 support importlib()?
    dir_tests_data: str = os.path.dirname(inspect.getfile(tests_data))

    # Copy all files from testing dir into the temporary testing dir.
    # Use inspect to get the actual path.
    # print("dir_tests_data:", dir_tests_data)
    test_dir_path = f"{dir_tests_data}/{test_dir}/"
    assert os.path.isdir(
        os.path.dirname(test_dir_path)
    ), f"Test directory not found: {test_dir}"
    # NOTE Next lines tested in: test_prep_config_copies_files()
    for f in Path(test_dir_path).glob("*"):
        if os.path.isfile(f):  # pragma: no branch
            shutil.copy(f, ".")

    # Make sure we have a default config file location.
    assert isinstance(s.DEFAULT_CONFIG_FILE, str)
    test_config_file: str = test_dir_path
    if config_file_override:
        print("Config file override:", config_file_override)
        test_config_file += config_file_override
        if not os.path.isfile(test_config_file):  # pragma: no cover
            print("Error: override config file not found at:", test_config_file)
            assert 1 == 0
        # Copy in this override file as the default config file.
        shutil.copy(test_config_file, s.DEFAULT_CONFIG_FILE)
    else:
        test_config_file += s.DEFAULT_CONFIG_FILE
    if not os.path.isfile(test_config_file):
        print("Warning: no config file found for this test at", test_config_file)
    if append_config:
        print("Appending config:", append_config)
        print(s.MSG_LINE)
        # NOTE mypy and open() don't seem to play well together
        # https://github.com/python/typeshed/issues/6076
        with open(os.fspath(s.DEFAULT_CONFIG_FILE), "a") as f:  # type: ignore
            f.write(append_config)  # type: ignore
    if print_config:  # pragma: no cover
        with open(s.DEFAULT_CONFIG_FILE) as f:  # type: ignore
            print(s.MSG_LINE_DOUBLE)
            print("CONFIG FILE:")
            shutil.copyfileobj(f, sys.stdout)  # type: ignore
            print(s.MSG_LINE_DOUBLE)


def string_as_config(config: str) -> bool:
    """Write a multiline string as the config file for a test.

    Intended for use within a temporary directory.
    """
    s = Settings()
    assert isinstance(s.DEFAULT_CONFIG_FILE, str)
    # Ensure we're not writing over an existing config file.
    assert not os.path.isfile(s.DEFAULT_CONFIG_FILE)
    with open(s.DEFAULT_CONFIG_FILE, "w") as f:  # type: ignore
        f.write(config)
    assert os.path.isfile(s.DEFAULT_CONFIG_FILE)
    return True


def process_test_tuples(test_config, runner):
    """Test a list of tuples.

    Tuple elements:
    0: expected exit code
    1: test dir
    2: expected message in result.output
    3: (optional) config file override


    """
    s = Settings()
    for test_tuple in test_config:
        exit_code: int = test_tuple[0]
        test_dir: str = test_tuple[1]
        msg: str = test_tuple[2]
        config_file_override: str = None
        try:
            config_file_override = test_tuple[3]
        except IndexError:
            pass
        print("test:", test_dir, f"{s.MSG_NL_TAB}msg:", msg)
        with runner.isolated_filesystem():
            prep_test_config(test_dir, config_file_override=config_file_override)
            result = runner.invoke(cli, [s.CMD_RUN])
            assert result.output.find(msg)
            assert result.exit_code == exit_code
