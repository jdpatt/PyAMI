from pyibisami.ami.parser import parse_ami_file

# pylint: disable=redefined-outer-name,protected-access


def test_parse_ami_param_defs(ami_test_file):
    error_string, param_defs = parse_ami_file(ami_test_file)
    assert error_string == ""
    assert param_defs["example_tx"]["description"] == "Example Tx model from ibisami package."
