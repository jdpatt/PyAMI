from pyibisami.ibis.parser import parse_ibis_file


def test_parse_ibis_file_with_ideal_file(ibis_test_file):
    """Test that pyibisami can parse the template 5.1 ibis model file."""
    status_string, ibis_dictionary = parse_ibis_file(ibis_test_file)
    assert status_string == "Success!"
    assert ibis_dictionary["file_name"] == "example_tx.ibs"
    assert ibis_dictionary["file_rev"] == "v0.1"
    assert ibis_dictionary["ibis_ver"] == 5.1
