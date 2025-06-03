"""A package of Python modules, used to configure and test IBIS-AMI models.

.. moduleauthor:: David Banas <capn.freako@gmail.com>

Original Author: David Banas <capn.freako@gmail.com>

Original Date:   3 July 2012

Copyright (c) 2012 by David Banas; All rights reserved World wide.
"""

from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as _get_version

from pyibisami.ami import AMIModel, AMIModelInitializer, AMIParamConfigurator
from pyibisami.ibis import IBISModel

__all__ = ["IBISModel", "AMIParamConfigurator", "AMIModelInitializer", "AMIModel"]

# Set PEP396 version attribute
try:
    __version__ = _get_version("PyIBIS-AMI")
except PackageNotFoundError as err:
    __version__ = f"{err} (dev)"

__date__ = "October 12, 2023"
__authors__ = "David Banas & David Patterson"
__copy__ = "Copyright (c) 2012 David Banas, 2019 David Patterson"
