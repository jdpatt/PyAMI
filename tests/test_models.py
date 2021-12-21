"""This module tests that pyibisami can parse whatever files are in the target directory.

You can change the target directory by setting or changing your `PYIBISAMI_TEST_MODELS` environment
variable.  If this variable is not found, it will default to the current working folder. If the
folder does not contain any of the right files, pytest will skip this test.
"""
import logging
import os
from pathlib import Path

import pytest

from pyibisami.ami.parser import parse_ami_file
from pyibisami.ibis.parser import parse_ibis_file


@pytest.fixture(scope="session")
def model_folder():
    folder = Path(os.getenv("PYIBISAMI_TEST_MODELS", default=""))
    print(f"Searching {folder.absolute()}")
    return folder


def test_parse_random_ibis_files(caplog, model_folder):
    """Test that `pyibisami` can parse any ibis model in the `PYIBISAMI_TEST_MODELS` test folder."""
    caplog.set_level(logging.DEBUG)
    ibis_files = list(model_folder.rglob("*.ibs"))
    if not ibis_files:
        pytest.skip(f"No IBIS files found in {model_folder}.")
    for filepath in ibis_files:
        parse_ibis_file(filepath)


def test_parse_random_ami_files(caplog, model_folder):
    """Test that `pyibisami` can parse any ami model in the `PYIBISAMI_TEST_MODELS` test folder."""
    caplog.set_level(logging.DEBUG)
    ami_files = list(model_folder.rglob("*.ami"))
    if not ami_files:
        pytest.skip(f"No AMI files found in {model_folder}.")
    for filepath in ami_files:
        parse_ami_file(filepath)
