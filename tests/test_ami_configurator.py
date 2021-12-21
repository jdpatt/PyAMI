import pytest

from pyibisami.ami.configurator import AMIParamConfigurator

# pylint: disable=redefined-outer-name,protected-access


def test_AMIParamConfigurator_without_GUI(ami_test_file):
    """Test that we can parse an AMI file and turn it into an ami object."""
    ami = AMIParamConfigurator(ami_test_file)
    assert ami._root_name == "example_tx"
    assert ami._ami_parsing_errors == ""
    test_keys = ("tx_tap_units", "tx_tap_np1", "tx_tap_nm1", "tx_tap_nm2")
    assert all(key in ami._param_dict["Model_Specific"] for key in test_keys)
    assert ami._param_dict["Model_Specific"]["tx_tap_units"].pvalue == 27
    assert ami._param_dict["Reserved_Parameters"]["AMI_Version"].pvalue == "5.1"


def test_no_model_specific_key(ami_test_file):
    """Test that an exception is raised when we get an invalid model key in the file."""
    with open(ami_test_file, encoding="UTF-8") as original_file:
        contents = original_file.read()
    edited_content = contents.replace("Model_Specific", "whoops")
    with open(ami_test_file, "w", encoding="UTF-8") as edited_file:
        edited_file.write(edited_content)
    with pytest.raises(KeyError):
        AMIParamConfigurator(ami_test_file)


def test_fetch_param_val(ami_test_file):
    ami = AMIParamConfigurator(ami_test_file)
    assert ami.fetch_param_val(["Reserved_Parameters", "Init_Returns_Impulse"])
    assert not ami.fetch_param_val(["Reserved_Parameters", "Bad Name"])
