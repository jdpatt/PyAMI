"""Definitions common to all PyIBIS-AMI modules.

Original author: David Banas <capn.freako@gmail.com>

Original date:   May 15, 2024

Copyright (c) 2024 David Banas; all rights reserved World wide.
"""

from typing import Any, Callable, NewType, TypeAlias, TypeVar

import numpy.typing as npt  # type: ignore

from pyibisami.ami.parameter import AMIParameter

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

# New types and aliases.
# Parameters  = NewType('Parameters',  dict[str, AMIParameter] | dict[str, 'Parameters'])
# ParamValues = NewType('ParamValues', dict[str, list[Any]]    | dict[str, 'ParamValues'])
# See: https://stackoverflow.com/questions/70894567/using-mypy-newtype-with-type-aliases-or-protocols
ParamName = NewType("ParamName", str)
ParamValue: TypeAlias = int | float | str | list["ParamValue"]
Parameters: TypeAlias = dict[ParamName, "'AMIParameter' | 'Parameters'"]
ParamValues: TypeAlias = dict[ParamName, "'ParamValue'   | 'ParamValues'"]

AmiName = NewType("AmiName", str)
AmiAtom: TypeAlias = bool | int | float | str
AmiExpr: TypeAlias = "'AmiAtom' | 'AmiNode'"
AmiNode: TypeAlias = tuple[AmiName, list[AmiExpr]]
AmiNodeParser: TypeAlias = Callable[[str], AmiNode]
AmiParser: TypeAlias = Callable[[str], tuple[AmiName, list[AmiNode]]]  # Atoms may not exist at the root level.

ParseErrMsg = NewType("ParseErrMsg", str)
AmiRootName = NewType("AmiRootName", str)
AmiReservedParameterName = NewType("AmiReservedParameterName", str)
ReservedParamDict: TypeAlias = dict[AmiReservedParameterName, AMIParameter]
ModelSpecificDict: TypeAlias = dict[ParamName, "'AMIParameter' | 'ModelSpecificDict'"]
