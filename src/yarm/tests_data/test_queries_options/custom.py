"""import for test_validate_complete_config_valid.yaml()."""
import pandas as pd


def test(data):
    """Test print function."""
    print("    ****** POSTPROCESS FUNCTION RUNS ******")
    return data


def wrong_args_1():
    """Wrong number of args."""
    return True


def wrong_args_2(data, second_required_arg):
    """Wrong number of args."""
    return True


def key_error(data):
    """Key Error."""
    data["new"] = data["this column doesn't exist"]
    return data


def return_other_type(data):
    """Other type."""
    return "df: Oops, this is a string."


def return_empty_df(data):
    """Return empty df."""
    return pd.DataFrame()


def other_type(data):
    """Other type."""
    return "df: Oops, this is a string."
