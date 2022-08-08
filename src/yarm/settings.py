#!/usr/bin/env python3

"""Settings class."""


class Settings:
    """Define global settings.

    When you need a setting in a function, make an instance
    of this class. These settings should NOT be changed; treat
    them as constants.
    """

    PKG = "yarm"
    DEFAULT_CONFIG_FILE: str = "report.yaml"
    DIR_TEMPLATES: str = "templates"
    DIR_TESTS_DATA: str = "tests_data"
    TEST_CONFIG_BAD_YAML: str = "test_config_bad_yaml.yaml"
    TEST_CONFIG_BAD_OPTIONS: str = "test_config_bad_options.yaml"
    CONFIG_SCHEMA = "config_schema.yaml"

    MSG_ABORT: str = "Aborted."
    MSG_SUCCESS: str = "Success!"
    MSG_WARN: str = "Warning:"
    MSG_USAGE: str = "Usage:"

    MSG_INVALID_CONFIG_NO_EDITS: str = (
        "This config file does not appear to have been edited."
    )
    MSG_INVALID_CONFIG_BAD_YAML: str = (
        "This config file has invalid YAML. Please fix the error below and try again."
    )
    MSG_COULDNT_OPEN_YAML: str = "Could not open YAML file."
    MSG_INVALID_CONFIG_BAD_OPTIONS: str = "This config file has misconfigured options."

    COLOR_ERROR: str = "red"
    COLOR_SUCCESS: str = "bright_green"
    COLOR_WARN: str = "bright_yellow"

    TEST_CUSTOM_CONFIG_FILE: str = "custom.yaml"
    CMD_RUN = "run"
