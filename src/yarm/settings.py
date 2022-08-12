#!/usr/bin/env python3

"""Settings class."""


class Settings:
    """Define global settings.

    When you need a setting in a function, make an instance
    of this class. These settings should NOT be changed; treat
    them as constants.
    """

    PKG = "yarm"
    DEFAULT_CONFIG_FILE: str = "yarm.yaml"
    DIR_TEMPLATES: str = "templates"
    DIR_TESTS_DATA: str = "tests_data"

    EXT_YAML: str = ".yaml"

    TEST_CONFIG_BAD_YAML: str = "test_config_bad_yaml"
    TEST_CONFIG_BAD_OPTIONS: str = "test_config_bad_options"

    MSG_ABORT: str = "Failed."
    MSG_SUCCESS: str = "Success!"
    MSG_WARN: str = "Warning:"
    MSG_USAGE: str = "Usage:"

    MSG_CONFIG_FILE_NOT_FOUND: str = "Could not find config file:"
    MSG_INVALID_CONFIG_NO_EDITS: str = (
        "This config file does not appear to have been edited."
    )
    MSG_INVALID_YAML: str = """This config file has invalid YAML or a misconfiguration.
Please fix the error below and try again."""
    MSG_PATH_NOT_FOUND: str = "One or more paths in your config could not be found:"
    MSG_VALIDATING_KEY: str = "Validating"
    MSG_CONFIG_FILE_VALID: str = "Configuration file validated: "

    COLOR_ERROR: str = "red"
    COLOR_SUCCESS: str = "bright_green"
    COLOR_WARN: str = "bright_yellow"
    COLOR_DATA: str = "bright_cyan"

    TEST_CUSTOM_CONFIG_FILE: str = "custom.yaml"
    CMD_RUN = "run"

    CONFIG_SCHEMA = "config_schema.yaml"
