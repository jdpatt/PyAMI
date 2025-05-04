import os
import pytest
from pathlib import Path
from pyibisami.ami.parser import parse_ami_file
from pyibisami.ibis.parser import parse_ibis_file


def get_ibis_files():
    """Get list of IBIS files from environment variable if it exists.

    If the environment variable PYIBISAMI_TEST_DIR is not set, the test will be skipped.
    We do not want to check in IBIS files to the repository, as they are large and may be under license restrictions.
    """
    ibis_dir = os.environ.get('PYIBISAMI_TEST_DIR')
    print(f"IBIS directory: {ibis_dir}")
    if not ibis_dir:
        return []

    ibis_dir = Path(ibis_dir)
    if not ibis_dir.exists():
        return []

    return [str(filepath) for filepath in ibis_dir.glob("**/*.ibs")]




@pytest.mark.skipif(not get_ibis_files(), reason='Either PYIBISAMI_TEST_DIR is not set or no IBIS files were found')
@pytest.mark.parametrize("ibis_file", get_ibis_files())
def test_external_ibis_file_parsing(ibis_file):
    """Test IBIS file parsing and model creation.

    If we find a matching AMI file, we check that the IBIS model's AMI file and it's model are generated correctly.

    The pytest.mark.parametrize will run this test once for each IBIS file found and report them as a test per line item
    in the terminal.
    """
    status, model = parse_ibis_file(ibis_file)
    assert status == "Success!"
    assert model is not None
