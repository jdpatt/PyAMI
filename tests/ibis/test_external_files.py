import os
import sys
from pathlib import Path

import pytest
from PySide6.QtWidgets import QComboBox, QDialogButtonBox

from pyibisami.ibis.model import IBISModel
from pyibisami.ibis.parser import parse_ibis_file


def get_ibis_files():
    """Get list of IBIS files from environment variable if it exists.

    If the environment variable PYIBISAMI_TEST_DIR is not set, the test will be skipped.
    We do not want to check in IBIS files to the repository, as they are large and may be under license restrictions.
    """
    ibis_dir = os.environ.get("PYIBISAMI_TEST_DIR")
    print(f"IBIS directory: {ibis_dir}")
    if not ibis_dir:
        return []

    ibis_dir = Path(ibis_dir)
    if not ibis_dir.exists():
        return []

    return [str(filepath.absolute()) for filepath in ibis_dir.glob("**/*.ibs")]


@pytest.mark.skipif(not get_ibis_files(), reason="Either PYIBISAMI_TEST_DIR is not set or no IBIS files were found")
@pytest.mark.parametrize("ibis_file", get_ibis_files())
def test_external_ibis_files(monkeypatch, qtbot, ibis_file):
    """Test IBIS file parsing and model creation.

    If we find a matching AMI file, we check that the IBIS model's AMI file and it's model are generated correctly.

    The pytest.mark.parametrize will run this test once for each IBIS file found and report them as a test per line item
    in the terminal.
    """
    # Patch sys.maxsize to simulate a 32-bit system
    monkeypatch.setattr(sys, "maxsize", 2**31 - 1)
    filepath = Path(ibis_file)
    model = parse_ibis_file(filepath)
    assert model is not None
    model["file_name"] = filepath
    assert model["components"] is not None
    assert model["models"] is not None
    assert model["model_selectors"] is not None

    ibis = IBISModel.from_dict(model, is_tx=True if "tx" in filepath.name else False)
    assert ibis is not None
    print(f"IBIS file: {ibis.ami_file.absolute()}")
    assert ibis.ami_file.exists()
    assert ibis.dll_file.exists()

    assert ibis.current_component is not None
    assert ibis.current_model is not None
    assert ibis.current_pin is not None

    # Test the GUI portion of the IBISModel class
    # Get GUI handle and show it
    gui = ibis.gui(get_handle=True)

    # Check model selector combobox has items
    model_combo = gui.model_combo
    assert model_combo is not None
    assert model_combo.count() > 0
