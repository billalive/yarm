"""Helper functions for tests."""
import inspect
import os
import shutil
from typing import List

from path import Path

from yarm import tests_data
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
    test_config_name: str, skip_config_file: bool = False, append_config: str = ""
) -> None:
    """Prepare test config file for a particular test.

    Several tests need a particular file in place as the config file
    for the test. This helper function sets that up.

    Use this helper function inside other tests.

    - Create the malformed config file in s.DIR_TESTS_DATA
      - Name it with only letters, numbers, and undescores.
      - Extension should be ".yaml"

    - Optional: If your test needs any supporting files, create a directory in
      tests_data/ with the same name as test_config_name. When this function is
      called with test_config_name, every file in this dir will also be copied
      into the temporary dir for this test. Note that when the test is run,
      these files will be in the *same* dir as the config file, so set the path
      accordingly in the config file.

    For example tests that use this function, see:

    - test_report_aborts_invalid_config_bad_yaml()
    - test_report_aborts_invalid_config_bad_options()
    - test_validate_config_mistakes()

    Args:
        test_config_name (str): basename of config file, without ".yaml"
        skip_config_file (bool): (optional) do not create config file.
        append_config (str): (optional) append this string as config
    """
    s = Settings()
    # Make sure we have a default config file location.
    dir_tests_data: str = os.path.dirname(inspect.getfile(tests_data))
    if not skip_config_file:
        assert isinstance(s.DEFAULT_CONFIG_FILE, str)
        # Copy in the config file for this test.
        # NOTE Is there a way to avoid hard-coding 'tests_data' here? Does it matter?
        # NOTE We use inspect() rather than importlib() to get this path, because
        # importlib has changed much more since 3.7, esp in how it handles dirs
        # within other dirs. Using inspect() to get the paths seems simpler.
        # TODO Since pandas requires 3.8, would 3.8 support importlib()?
        test_config_file: str = f"{dir_tests_data}/{test_config_name}{s.EXT_YAML}"
        assert os.path.isfile(test_config_file)
        shutil.copy(test_config_file, s.DEFAULT_CONFIG_FILE)
        if append_config:
            print("Appending config:", append_config)
            print(s.MSG_LINE)
            with open(s.DEFAULT_CONFIG_FILE, "a") as f:
                f.write(append_config)
        assert os.path.isfile(s.DEFAULT_CONFIG_FILE)
    if skip_config_file and append_config:
        print("Error: Can't use both 'skip_config' and 'append_config' in same test.")
        assert 1 == 0

    # Does this test have a test directory?
    # If so, copy all files from that dir into the temporary testing dir.
    # Use inspect to get the actual path.
    # print("dir_tests_data:", dir_tests_data)
    assert os.path.isdir(os.path.dirname(dir_tests_data))
    dir_test_config_name: str = f"{dir_tests_data}/{test_config_name}"
    # NOTE Next lines tested in: test_prep_config_copies_files()
    if os.path.isdir(os.path.dirname(dir_test_config_name)):  # pragma: no branch
        # print("is a dir:", dir_test_config_name)
        for f in Path(dir_test_config_name).glob("*"):
            if os.path.isfile(f):  # pragma: no branch
                shutil.copy(f, ".")
                # print("copying in:", f)
    # else:
    # print("not a dir:", dir_test_config_name)


def string_as_config(config: str) -> bool:
    """Write a multiline string as the config file for a test.

    Intended for use within a temporary directory.
    """
    s = Settings()
    assert isinstance(s.DEFAULT_CONFIG_FILE, str)
    # Ensure we're not writing over an existing config file.
    assert not os.path.isfile(s.DEFAULT_CONFIG_FILE)
    with open(s.DEFAULT_CONFIG_FILE, "w") as f:
        f.write(config)
    assert os.path.isfile(s.DEFAULT_CONFIG_FILE)
    return True
