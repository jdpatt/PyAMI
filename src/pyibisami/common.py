"""
Definitions common to all PyIBIS-AMI modules.

Original author: David Banas <capn.freako@gmail.com>

Original date:   May 15, 2024

Copyright (c) 2024 David Banas; all rights reserved World wide.
"""

from typing import Any, TypeAlias, TypeVar

import numpy.typing as npt  # type: ignore
from scipy.linalg import convolution_matrix, lstsq

Real = TypeVar("Real", float, float)
Comp = TypeVar("Comp", complex, complex)
Rvec: TypeAlias = npt.NDArray["Real"]
Cvec: TypeAlias = npt.NDArray["Comp"]

PI: float = 3.141592653589793238462643383279502884
TWOPI: float = 2.0 * PI

# TestConfig: TypeAlias = tuple[str, tuple[dict[str, Any], dict[str, Any]]]
# TestSweep:  TypeAlias = tuple[str, str, list[TestConfig]]
TestConfig = tuple[str, tuple[dict[str, Any], dict[str, Any]]]
TestSweep = tuple[str, str, list[TestConfig]]
