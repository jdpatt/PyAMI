import pytest

from pyibisami.ibis.parser import (
    IBISFileParsingError,
    MalformedIBISFileError,
    parse_ibis_file,
    parse_ibis_string,
    validate_ibis_model,
)


def test_parse_ibis_file_with_ideal_file(ibis_test_file):
    """Test that pyibisami can parse the template 5.1 ibis model file."""
    ibis_dictionary = parse_ibis_file(ibis_test_file)
    assert ibis_dictionary["file_name"] == "example_tx.ibs"
    assert ibis_dictionary["file_rev"] == "v0.1"
    assert ibis_dictionary["ibis_ver"] == 5.1
    assert len(ibis_dictionary["components"]) == 1
    assert len(ibis_dictionary["models"]) == 1


def test_parse_ibis_file_with_malformed_file(ibis_test_file):
    """Test that pyibisami can parse the template 5.1 ibis model file."""
    with open(ibis_test_file, "r") as f:
        lines = f.readlines()
    lines[2] = "[END]"  # Put END at the beginning of the file
    with pytest.raises(IBISFileParsingError):
        results = parse_ibis_string(lines)
        assert results is None


def test_parse_validator():
    """Test that the parse validator raises an error when the file is malformed."""
    with pytest.raises(MalformedIBISFileError):
        model_dict = {
            "file_name": "example_tx.ibs",
            "file_rev": "v0.1",
            "ibis_ver": 5.1,
            "components": [],
            "models": [],
        }
        validate_ibis_model(model_dict)
