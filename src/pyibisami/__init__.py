"""
A package of Python modules for using, configuring and testing IBIS-AMI models.

.. moduleauthor:: David Banas <capn.freako@gmail.com>

Original Author: David Banas <capn.freako@gmail.com>

Original Date:   3 July 2012

Copyright (c) 2012 by David Banas; All rights reserved World wide.
"""
import logging
from pkg_resources import DistributionNotFound, get_distribution

__date__ = "December 12, 2021"
__authors__ = "David Banas"
__copy__ = "Copyright (c) 2014 David Banas"

logging.getLogger("pyibisami").addHandler(logging.NullHandler())

try:
    __version__ = get_distribution("pyibisami").version
except DistributionNotFound:
    # package is not installed
    pass
