"""import for test_validate_complete_config_valid.yaml()."""


def test(data):
    """Test print function."""
    print("    ****** POSTPROCESS FUNCTION RUNS (MODULE_B) ******")
    data["test"] = data["id"] * 10
    return data
