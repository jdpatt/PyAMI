import pytest

from pyibisami.ami_parameter import AMIParamError


def test_AMIParamError():
    with pytest.raises(Exception):
        raise AMIParamError("test")
