#!/usr/bin/env python3

# noqa: B950

"""Validate config file."""

import importlib.resources as pkg_resources
from typing import Any
from typing import Dict

import yaml

from yarm.helpers import abort

# from yarm.helpers import success
# from yarm.helpers import warn
# from yarm.helpers import yaml_to_dict
from yarm.settings import Settings


# from typing import List


# from yarm.helpers import echo_verbose


def validate_config(config: Dict[Any, Any]) -> bool:
    """Validate config file before running report."""
    # Why no test whether file exists? click() handles this.

    # DEBUG:
    # for key in config:
    #    print(key, config[key])

    validate_config_edited(config)
    validate_config_schema(config)

    # Check whether config options are valid.

    # If all tests pass, config file is validated.
    return True


def validate_config_edited(config: Dict[Any, Any]) -> bool:
    """Check whether config has been edited."""
    # Rather than an exhaustive search, just check a critical setting.
    s = Settings()
    default_config = get_default_config()
    if config["output"]["basename"] == default_config["output"]["basename"]:
        abort(
            f"""{s.MSG_INVALID_CONFIG_NO_EDITS}

output.basename is still set to the default: {default_config["output"]["basename"]}

Please edit your config file, then try running this report again.
"""
        )
        return False
    return True


def validate_config_schema(config: Dict[Any, Any]) -> bool:
    """Check whether config options are valid."""
    # config_schema = get_config_schema()
    return True


def get_default_config() -> Any:
    """Get default config."""
    s = Settings()
    return yaml.safe_load(
        pkg_resources.read_text(f"{s.PKG}.{s.DIR_TEMPLATES}", s.DEFAULT_CONFIG_FILE),
    )


def get_config_schema() -> Any:
    """Get 'schema' of config options.

    When you add an option, you must add it to this template file,
    so that validate_config_schema() will recognize it.

    An UPPERCASE value means that the user can define their own custom name.
    E.g. TABLE_NAME.

    NONE_OR_STR means that the user can either provide a string or leave this
    blank.

    tables_config and create_tables should have identical options.

    Except: where tables_config has TABLE_NAME, create_tables has NONE_OR_LIST.
    This allows you to define a table fully

    They are separate so that you can include a config file with a tables_config
    that defines ALL the tables you often use, but then use create_tables to only
    actually create the specific tables you need for this report.
    """
    s = Settings()
    return yaml.safe_load(
        pkg_resources.read_text(f"{s.PKG}.{s.DIR_TEMPLATES}", s.CONFIG_SCHEMA),
    )


def get_first_dict_key(dict_to_extract: Dict[Any, Any]) -> Any:
    """Return the first key in a dictionary."""
    return list(dict_to_extract.items())[0][0]
