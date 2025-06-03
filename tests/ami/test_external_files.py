import os
from pathlib import Path

import pytest

from pyibisami.ami.model import AMIParamConfigurator
from pyibisami.ami.parser import parse_ami_file


def get_ami_files():
    """Get list of AMI files from environment variable if it exists.

    If the environment variable PYIBISAMI_TEST_DIR is not set, the test will be skipped. We do not want to check in AMI
    files to the repository, as they are large and may be under license restrictions.
    """
    ami_dir = os.environ.get("PYIBISAMI_TEST_DIR")
    print(f"AMI directory: {ami_dir}")
    if not ami_dir:
        return []

    ami_dir = Path(ami_dir)
    if not ami_dir.exists():
        return []

    # Convert it to a string so that pytest shows the filepath vs a path object.
    return [str(filepath) for filepath in ami_dir.glob("**/*.ami")]


@pytest.mark.skipif(not get_ami_files(), reason="Either PYIBISAMI_TEST_DIR is not set or no AMI files were found")
@pytest.mark.parametrize("ami_file", get_ami_files())
def test_external_ami_file_parsing(qtbot, ami_file):
    """Test AMI file parsing."""
    ami_file = Path(ami_file)  # Turn it back into a filepath after pytest collection.
    errors, root_name, description, reserved_params, model_specific_params = parse_ami_file(ami_file)
    assert errors == ""
    assert len(root_name) > 0
    assert len(reserved_params) > 0
    assert len(model_specific_params) > 0

    ami_config = AMIParamConfigurator.from_file(ami_file)

    gui = ami_config.gui(get_handle=True)
    values, params = gui.get_values()
    assert values is not None
