"""IBIS-AMI parameter parsing and configuration utilities.

Original author: David Banas <capn.freako@gmail.com>

Original date:   December 17, 2016

Copyright (c) 2019 David Banas; all rights reserved World wide.
"""

import logging
import re
from pathlib import Path

from parsec import ParseError, generate, many, regex, string

from pyibisami.ami.parameter import AMIParamError, AMIParameter
from pyibisami.ami.reserved_parameter_names import RESERVED_PARAM_NAMES
from pyibisami.common import (
    AmiParser,
    AmiRootName,
    ModelSpecificDict,
    ParseErrMsg,
    ReservedParamDict,
)

logger = logging.getLogger("pyibisami.ami")


class AMIFileParsingError(Exception):
    """Exception raised for errors in AMI file parsing."""


class MalformedAMIFileError(AMIFileParsingError):
    """Exception raised for errors in AMI file parsing."""


# Pre-compile regex patterns as ALL_CAPS constants for efficiency and consistency.
RE_WHITESPACE = re.compile(r"\s+", re.MULTILINE)
RE_COMMENT = re.compile(r"\|.*")
RE_NUMBER = re.compile(r"[-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?")
RE_INTEG = re.compile(r"[-+]?[0-9]+")
RE_NAT = re.compile(r"[0-9]+")
RE_SYMBOL = re.compile(r"[0-9a-zA-Z_][^\s()]*")
RE_AMI_STRING = re.compile(r'"[^"]*"')

# ignore cases.
whitespace = regex(RE_WHITESPACE)
comment = regex(RE_COMMENT)
ignore = many(whitespace | comment)


def lexeme(p):
    """Lexer for words."""
    return p << ignore  # skip all ignored characters.


def int2tap(x):
    """Convert integer to tap position."""
    x = x.strip()
    if x[0] == "-":
        res = "pre" + x[1:]
    else:
        res = "post" + x
    return res


lparen = lexeme(string("("))
rparen = lexeme(string(")"))
number = lexeme(regex(RE_NUMBER))
integ = lexeme(regex(RE_INTEG))
nat = lexeme(regex(RE_NAT))
tap_ix = (integ << whitespace).parsecmap(int2tap)
symbol = lexeme(regex(RE_SYMBOL))
true = lexeme(string("True")).result(True)
false = lexeme(string("False")).result(False)
ami_string = lexeme(regex(RE_AMI_STRING))

atom = number | symbol | ami_string | (true | false)
node_name = tap_ix ^ symbol  # `tap_ix` is new and gives the tap position; negative positions are allowed.


@generate("AMI node")
def node():
    "Parse AMI node."
    yield lparen
    label = yield node_name
    values = yield many(expr)
    yield rparen
    return (label, values)


@generate("AMI file")
def root():
    "Parse AMI file."
    yield lparen
    label = yield node_name
    values = yield many(node)
    yield rparen
    return (label, values)


expr = atom | node
ami = ignore >> root
ami_parse: AmiParser = ami.parse


def proc_branch(branch):
    """Process a branch in a AMI parameter definition tree.

    That is, build a dictionary from a pair containing:
        - a parameter name, and
        - a list of either:
            - parameter definition tags, or
            - subparameters.

    We distinguish between the two possible kinds of payloads, by
    peaking at the names of the first two items in the list and noting
    whether they are keys of 'AMIParameter._param_def_tag_procs'.
    We have to do this twice, due to the dual use of the 'Description'
    tag and the fact that we have no guarantee of any particular
    ordering of subparameter branch items.

    Args:
        p (str, list): A pair, as described above.

    Returns:
        (str, dict): A pair containing:
            err_str: String containing any errors or warnings encountered,
                while building the parameter dictionary.
            param_dict: Resultant parameter dictionary.
    """
    results = ("", {})  # Empty Results
    if len(branch) != 2:
        if not branch:
            err_str = "ERROR: Empty branch provided to proc_branch()!\n"
        else:
            err_str = f"ERROR: Malformed item: {branch[0]}\n"
        results = (err_str, {})

    param_name = branch[0]
    param_tags = branch[1]

    if not param_tags:
        err_str = f"ERROR: No tags/subparameters provided for parameter, '{param_name}'\n"
        results = (err_str, {})

    try:
        if (
            (len(param_tags) > 1)
            and (  # noqa: W503
                param_tags[0][0] in AMIParameter._param_def_tag_procs  # pylint: disable=protected-access  # noqa: W503
            )
            and (  # noqa: W503
                param_tags[1][0] in AMIParameter._param_def_tag_procs  # pylint: disable=protected-access  # noqa: W503
            )
        ):
            try:
                results = ("", {param_name: AMIParameter(param_name, param_tags)})
            except AMIParamError as err:
                results = (str(err), {})
        elif param_name == "Description":
            results = ("", {"description": param_tags[0].strip('"')})
        else:
            err_str = ""
            param_dict = {}
            param_dict[param_name] = {}
            for param_tag in param_tags:
                temp_str, temp_dict = proc_branch(param_tag)
                param_dict[param_name].update(temp_dict)
                if temp_str:
                    err_str = (
                        f"Error returned by recursive call, while processing parameter, '{param_name}':\n{temp_str}"
                    )
                    results = (err_str, param_dict)

            results = (err_str, param_dict)
    except Exception:  # pylint: disable=broad-exception-caught
        print(f"Error processing branch:\n{param_tags}")
    return results


def parse_ami_string(  # pylint: disable=too-many-locals,too-many-branches
    ami_string: str,
) -> tuple[ParseErrMsg, AmiRootName, str, ReservedParamDict, ModelSpecificDict]:
    """
    Parse the contents of an IBIS-AMI *parameter definition* (i.e. - `*.ami`) file.

    Args:
        ami_string: The contents of the AMI file, as a single string.

    Example:
        >>>  (err_str, root_name, reserved_param_dict, model_specific_param_dict) = parse_ami_string(ami_string)

    Returns:
        A tuple containing

            1. Any error message generated by the parser. (empty on success)

            2. AMI file "root" name.

            3. *Reserved Parameters* dictionary. (empty on failure)

                - The keys of the *Reserved Parameters* dictionary are
                limited to those called out in the IBIS-AMI specification.

                - The values of the *Reserved Parameters* dictionary
                must be instances of class ``AMIParameter``.

            4. *Model Specific Parameters* dictionary. (empty on failure)

                - The keys of the *Model Specific Parameters* dictionary can be anything.

                - The values of the *Model Specific Parameters* dictionary
                may be either: an instance of class ``AMIParameter``, or a nested sub-dictionary.
    """
    try:
        res = ami_parse(ami_string)
    except ParseError as pe:
        raise AMIFileParsingError(f"Expected {pe.expected} at {pe.loc()} in:\n{pe.text[pe.index:]}") from pe

    err_str, param_dict = proc_branch(res)
    if err_str:
        return (err_str, AmiRootName(""), "", {}, {})
    if len(param_dict.keys()) != 1:
        raise MalformedAMIFileError(f"Malformed AMI parameter S-exp has top-level keys: {param_dict.keys()}!")

    reserved_found = False
    init_returns_impulse_found = False
    getwave_exists_found = False
    model_spec_found = False
    root_name, params = list(param_dict.items())[0]
    description = ""
    reserved_params_dict = {}
    model_specific_dict = {}
    _err_str = ""
    for label in list(params.keys()):
        tmp_params = params[label]
        if label == "Reserved_Parameters":
            reserved_found = True
            for param_name in list(tmp_params.keys()):
                if param_name not in RESERVED_PARAM_NAMES:
                    _err_str += f"WARNING: Unrecognized reserved parameter name, '{param_name}', found in parameter definition string!\n"
                    continue
                param = tmp_params[param_name]
                if param.pname == "AMI_Version":
                    if param.pusage != "Info" or param.ptype != "String":
                        _err_str += "WARNING: Malformed 'AMI_Version' parameter.\n"
                elif param.pname == "Init_Returns_Impulse":
                    init_returns_impulse_found = True
                elif param.pname == "GetWave_Exists":
                    getwave_exists_found = True
            reserved_params_dict = tmp_params
        elif label == "Model_Specific":
            model_spec_found = True
            model_specific_dict = tmp_params
        elif label == "description":
            description = str(tmp_params)
        else:
            _err_str += f"WARNING: Unrecognized group with label, '{label}', found in parameter definition string!\n"

    if not reserved_found:
        _err_str += "ERROR: Reserved parameters section not found! It is required."

    if not init_returns_impulse_found:
        _err_str += "ERROR: Reserved parameter, 'Init_Returns_Impulse', not found! It is required."

    if not getwave_exists_found:
        _err_str += "ERROR: Reserved parameter, 'GetWave_Exists', not found! It is required."

    if not model_spec_found:
        _err_str += "WARNING: Model specific parameters section not found!"

    return (ParseErrMsg(_err_str), root_name, description, reserved_params_dict, model_specific_dict)


def parse_ami_file(
    ami_file_path: str | Path,
) -> tuple[ParseErrMsg, AmiRootName, str, ReservedParamDict, ModelSpecificDict]:
    """Parse the contents of an AMI file.

    Args:
        ami_file_path (str | Path): The name of the AMI file.
    Example:
        >>> model_dict = parse_ami_file(ami_file_path)
    Returns:
    """
    with open(ami_file_path, "r", encoding="utf-8") as ami_file:
        ami_string = ami_file.read()
    return parse_ami_string(ami_string)
