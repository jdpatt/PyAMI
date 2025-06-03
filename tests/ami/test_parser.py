import pytest

from pyibisami.ami.parser import AMIFileParsingError, parse_ami_string


@pytest.fixture
def test_ami_config():
    return r"""(example_tx

    (Description "Example Tx model from ibisami package.")

    (Reserved_Parameters
         (AMI_Version
             (Usage Info )
             (Type String )
             (Value "5.1" )
             (Description "Version of IBIS standard we comply with." )
         )
         (Init_Returns_Impulse
             (Usage Info )
             (Type Boolean )
             (Value True )
             (Description "In fact, this model is, currently, Init-only." )
         )
         (GetWave_Exists
             (Usage Info )
             (Type Boolean )
             (Value True )
             (Description "This model is dual-mode, with GetWave() mimicking Init()." )
         )
    )
    (Model_Specific
         (tx_tap_units
             (Usage In )
             (Type Integer )
             (Range 27 6 27 )
             (Description "Total current available to FIR filter." )
         )
         (tx_tap_np1
             (Usage In )
             (Type Integer )
             (Range 0 0 10 )
             (Description "First (and only) pre-tap." )
         )
         (tx_tap_nm1
             (Usage In )
             (Type Integer )
             (Range 0 0 10 )
             (Description "First post-tap." )
         )
         (tx_tap_nm2
             (Usage In )
             (Type Integer )
             (Range 0 0 10 )
             (Description "Second post-tap." )
         )
    )

)

"""


def test_parse_ami_string(test_ami_config):
    """Test that pyibisami can parse the template AMI model file."""
    error_string, root_name, description, reserved_params_dict, model_specific_dict = parse_ami_string(test_ami_config)
    assert error_string == ""
    assert root_name == "example_tx"
    assert description == "Example Tx model from ibisami package."


@pytest.mark.xfail(reason="The parser still just returns strings for now.")
def test_parse_ami_string_with_malformed_file(test_ami_config):
    """When we don't have a Model_Specific key, we should get an error."""
    edited = test_ami_config.replace("Model_Specific", "whoops")
    with pytest.raises(AMIFileParsingError):
        parse_ami_string(edited)
