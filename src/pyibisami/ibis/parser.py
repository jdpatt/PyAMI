"""Parse an IBIS model file.

Original Author: David Banas <capn.freako@gmail.com>

Original Date:   November 1, 2019

For information regarding the IBIS modeling standard, visit:
https://ibis.org/

Copyright (c) 2019 by David Banas; All rights reserved World wide.
"""

import logging
import re
from pathlib import Path

from parsec import (
    ParseError,
    Parser,
    count,
    eof,
    fail_with,
    generate,
    letter,
    many,
    many1,
    none_of,
    one_of,
    optional,
    regex,
    separated,
    sepBy1,
    string,
    times,
)

logger = logging.getLogger("pyibisami.ibis.parser")

# Compile regex patterns at module level
RE_WHITESPACE = re.compile(r"\s+", re.MULTILINE)
RE_COMMENT = re.compile(r"\|.*")  # To end of line only.
RE_NAME_ONLY = re.compile(r"[_a-zA-Z0-9/\.()#-]+")
RE_SYMBOL = re.compile(r"[a-zA-Z_][^\s()\[\]]*")
RE_QUOTED_STRING = re.compile(r'"[^"]*"')
RE_NUMBER = re.compile(r"[-+]?[0-9]*\.?[0-9]+(([eE][-+]?[0-9]+)|([TknGmpMuf][a-zA-Z]*))?")


class IBISFileParsingError(Exception):
    """Exception raised for errors in IBIS file parsing."""

    pass


class MalformedIBISFileError(Exception):
    """Exception raised for errors in IBIS file parsing."""

    pass


# Parser Definitions
whitespace = regex(RE_WHITESPACE)
comment = regex(RE_COMMENT)
ignore = many(whitespace | comment)  # None is okay; so, can be used completely safely.


def logf(p: Parser, preStr: str = "") -> Parser:
    """
    Returns parser ``p`` wrapped in a thin shell, which logs any failure at the point of occurrence.

    Args:
        p: The original parser.

    Keyword Args:
        preStr: A prefix string to use in failure message.
            (Default = <empty string>)

    Returns:
        p': The original parser wrapped in a thin failure location shell.
    """

    @Parser
    def fn(txt, ix):
        res = p(txt, ix)
        if not res.status:
            logger.error(
                "%s: Expected `%s` in `%s` at %s.",
                preStr,
                res.expected,
                txt[res.index : res.index + 5],
                ParseError.loc_info(txt, res.index),
            )
        return res

    return fn


def lexeme(p):
    """Lexer for words.

    Skips all ignored characters after word, including newlines.
    """
    return p << ignore


def word(p):
    """Line limited word lexer.

    Only skips space after words; doesn't skip comments or newlines.
    Requires, at least, one white space character after word.
    """
    return p << regex(r"\s+")


@generate("remainder of line")
def rest_line():
    "Parse remainder of line."
    chars = yield many(none_of("\n\r")) << ignore  # So that we still function as a lexeme.
    return "".join(chars)


skip_line = lexeme(rest_line).result("(Skipped.)")
name_only = regex(RE_NAME_ONLY)
name = word(name_only)
symbol = lexeme(regex(RE_SYMBOL))
true = lexeme(string("True")).result(True)
false = lexeme(string("False")).result(False)
quoted_string = lexeme(regex(RE_QUOTED_STRING))
skip_keyword = (skip_line >> many(none_of("[") >> skip_line)).result(
    "(Skipped.)"
)  # Skip over everything until the next keyword begins.

IBIS_num_suf = {
    "T": "e12",
    "k": "e3",
    "n": "e-9",
    "G": "e9",
    "m": "e-3",
    "p": "e-12",
    "M": "e6",
    "u": "e-6",
    "f": "e-15",
}


@generate("number")
def number():
    "Parse an IBIS numerical value."
    s = yield (regex(RE_NUMBER) << many(letter()) << ignore)
    m = re.search(r"[^\d]+$", s)
    if m:
        ix = m.start()
        c = s[ix]
        if c in IBIS_num_suf:
            res = float(s[:ix] + IBIS_num_suf[c])
        else:
            raise ParseError("IBIS numerical suffix", s[ix:], ix)
    else:
        res = float(s)
    return res


na = word(string("NA") | string("na")).result(None)


@generate("typminmax")
def typminmax():
    "Parse Typ/Min/Max values."
    typ = yield number
    minmax = yield optional(count(number, 2) | count(na, 2).result([]), [])
    yield ignore  # So that ``typminmax`` behaves as a lexeme.
    res = [typ]
    res.extend(minmax)
    return res


vi_line = (number + typminmax) << ignore


@generate("ratio")
def ratio():
    "Parse ratio."
    [num, den] = yield (separated(number, string("/"), 2, maxt=2, end=False) | na.result([0, 0]))
    if den:
        return num / den
    return None


ramp_line = string("dV/dt_") >> ((string("r").result("rising") | string("f").result("falling")) << ignore) + times(
    ratio, 1, 3
)
ex_line = (
    word(string("Executable"))
    >> (  # noqa: W503
        (
            ((string("L") | string("l")) >> string("inux")).result("linux")
            | ((string("W") | string("w")) >> string("indows")).result("windows")  # noqa: W503
        )
        << string("_")  # noqa: W503
        << many(none_of("_"))  # noqa: W503
        << string("_")  # noqa: W503
    )
    + lexeme(string("32") | string("64"))  # noqa: W503
    + count(name, 2)  # noqa: W503
    << ignore  # noqa: W503
)


def manyTrue(p):
    "Run a parser multiple times, filtering ``False`` results."

    @generate("manyTrue")
    def fn():
        "many(p) >> filter(True)"
        nodes = yield many(p)
        res = list(filter(None, nodes))
        return res

    return fn


def many1True(p):
    "Run a parser at least once, filtering ``False`` results."

    @generate("many1True")
    def fn():
        "many1(p) >> filter(True)"
        nodes = yield many1(p)
        res = list(filter(None, nodes))
        return res

    return fn


# IBIS file parser:


def keyword(kywrd=""):
    """Parse an IBIS keyword.

    Keyword Args:
        kywrd (str): The particular keyword to match; null for any keyword.
            If provided, *must* be in canonicalized form (i.e. - underscores,
            no spaces)!

    Returns:
        Parser: A keyword parser.
    """

    @generate("IBIS keyword")
    def fn():
        "Parse IBIS keyword."
        yield regex(r"^\[", re.MULTILINE)
        wordlets = yield sepBy1(name_only, one_of(" _"))  # ``name`` gobbles up trailing space, which we don't want.
        yield string("]")
        yield ignore  # So that ``keyword`` functions as a lexeme.
        res = "_".join(wordlets)  # Canonicalize to: "<wordlet1>_<wordlet2>_...".
        if kywrd:
            if res.lower() == kywrd.lower():
                return res
            return fail_with(f"Expecting: {kywrd}; got: {res}.")
        return res

    return fn


@generate("IBIS parameter")
def param():
    """Parse IBIS parameter."""
    # Parameters must begin with a letter in column 1.
    pname = yield word(regex(r"^[a-zA-Z]\w*", re.MULTILINE))
    logger.debug("Parsing parameter %s...", pname)
    res = yield ((word(string("=")) >> (number | rest_line)) | typminmax | name | rest_line)
    logger.debug(res)
    yield ignore  # So that ``param`` functions as a lexeme.
    return (pname.lower(), res)


def node(valid_keywords, stop_keywords):
    """Build a node-specific parser.

    Args:
        valid_keywords (dict): A dictionary with keys matching those
            keywords we want parsed. The values are the parsers for
            those keywords.
        stop_keywords: Any iterable with primary values (i.e. - those
            tested by the ``in`` function) matching those keywords we want
            to stop the parsing of this node and pop us back up the
            parsing stack.

    Returns:
        Parser: A parser for this node.

    Notes:
        1: Any keywords encountered that are _not_ found (via ``in``) in
            either ``valid_keywords`` or ``stop_keywords`` are ignored.
    """

    @generate("kywrd")
    def kywrd():
        "Parse keyword syntax."
        nm = yield keyword()
        nmL = nm.lower()
        logger.debug("Parsing keyword: [{%s}]...", nm)
        if nmL in valid_keywords:
            if nmL == "end":  # Because ``ibis_file`` expects this to be the last thing it sees,
                return fail_with("")  # we can't consume it here.
            res = yield logf(valid_keywords[nmL], f"[{nm}]")  # Parse the sub-keyword.
        elif nmL in stop_keywords:
            return fail_with("")  # Stop parsing.
        else:
            res = yield skip_keyword
        yield ignore  # So that ``kywrd`` behaves as a lexeme.
        logger.debug("Finished parsing keyword: [{%s}].", nm)
        return (nmL, res)

    return kywrd | param


# Individual IBIS keyword (i.e. - "node") parsers:


# [End]
@generate("[End]")
def end():
    """Parse [End]."""
    yield keyword("End")
    return eof


# [Model]
@generate("[Ramp]")
def ramp():
    """Parse [Ramp]."""
    lines = yield count(ramp_line, 2).desc("Two ramp_lines")
    return dict(lines)  # .update(dict(params))


Model_keywords = {
    "pulldown": many1(vi_line),
    "pullup": many1(vi_line),
    "ramp": ramp,
    "algorithmic_model": many1(ex_line) << keyword("end_algorithmic_model"),
    "voltage_range": typminmax,
    "temperature_range": typminmax,
    "gnd_clamp": many1(vi_line),
    "power_clamp": many1(vi_line),
}


@generate("[Model]")
def model():
    """Parse [Model]."""
    nm = yield name << ignore
    logger.debug("Parsing model: %s...", nm)
    res = yield many1(node(Model_keywords, IBIS_keywords))
    logger.debug("[Model] %s contains: %s", nm, dict(res).keys())
    try:
        theModel = dict(res)
    except LookupError as le:
        return fail_with(f"[Model] {nm}: {str(le)}")
    return {nm: theModel}


# [Component]
rlc = lexeme(string("R_pin") | string("L_pin") | string("C_pin"))


@generate("[Package]")
def package():
    """Parse package RLC values."""
    rlcs = yield many1(param)
    logger.debug("rlcs: %s", rlcs)
    return dict(rlcs)


def pin(rlcs):
    """Parse individual component pin."""

    @generate("Component Pin")
    def fn():
        """Parse an individual component pin."""
        [nm, sig] = yield count(name, 2)
        mod = yield name_only
        rem_line = yield rest_line
        rlc_vals = optional(count(number, 3), []).parse(rem_line)
        rlc_dict = {}
        if rlcs:
            rlc_dict.update(dict(zip(rlcs, rlc_vals)))
        return ((nm + "(" + sig + ")"), (mod, rlc_dict))

    return fn


@generate("[Component].[Pin]")
def pins():
    """Parse [Component].[Pin]."""

    def filt(x):
        (_, (mod, _)) = x
        m = mod.upper()
        return m not in ("POWER", "GND", "NC")

    yield (lexeme(string("signal_name")) << lexeme(string("model_name")))
    rlcs = yield optional(count(rlc, 3), [])
    prs = yield many1(pin(rlcs))
    prs_filt = list(filter(filt, prs))
    return dict(prs_filt)


Component_keywords = {
    "manufacturer": rest_line,
    "package": package,
    "pin": pins,
    "diff_pin": skip_keyword,
}


@generate("[Component]")
def comp():
    """Parse [Component]."""
    nm = yield lexeme(name)
    logger.debug("Parsing component: %s", nm)
    res = yield many1(node(Component_keywords, IBIS_keywords))
    try:
        component = dict(res)
    except LookupError as le:
        return fail_with(f"[Component] {nm}: {str(le)}")
    except Exception as err:  # pylint: disable=broad-exception-caught
        return fail_with(f"[Component] {nm}: {str(err)}")
    return {nm: component}


@generate("[Model Selector]")
def modsel():
    """Parse [Model Selector]."""
    nm = yield name
    res = yield ignore >> many1(name + rest_line)
    return {nm: res}


# Note: The following list MUST have a complete set of keys,
#       in order for the parsing logic to work correctly!
IBIS_keywords = [
    "model",
    "end",
    "ibis_ver",
    "comment_char",
    "file_name",
    "file_rev",
    "date",
    "source",
    "notes",
    "disclaimer",
    "copyright",
    "component",
    "model_selector",
    "submodel",
    "external_circuit",
    "test_data",
    "test_load",
    "define_package_model",
    "interconnect_model_set",
]

IBIS_kywrd_parsers = dict(zip(IBIS_keywords, [skip_keyword] * len(IBIS_keywords)))
IBIS_kywrd_parsers.update(
    {
        "model": model,
        "end": end,
        "ibis_ver": lexeme(number),
        "file_name": lexeme(name),
        "file_rev": lexeme(name),
        "date": rest_line,
        "component": comp,
        "model_selector": modsel,
    }
)


@generate("IBIS File")
def ibis_file():
    """Parse IBIS file."""
    res = yield ignore >> many1True(node(IBIS_kywrd_parsers, {})) << end
    return res


def parse_ibis_string(ibis_string: str) -> dict:
    """Parse the contents of an IBIS string into a dictionary.

    Args:
        ibis_string (str): The contents of an IBIS file.

    Returns:
        model_dict: Dictionary containing keyword definitions (empty upon failure).
    """
    try:
        nodes = ibis_file.parse_strict(ibis_string)  # Parse must consume the entire file.
        logger.debug("Parsed nodes:\n%s", nodes)
    except ParseError as pe:
        logger.warning("IBIS parsing errors/warnings: %s", str(pe))
        raise IBISFileParsingError(f"IBIS parsing errors/warnings: {str(pe)}") from pe

    kw_dict = {}
    components = {}
    models = {}
    model_selectors = {}
    for kw, val in nodes:
        if kw == "model":
            models.update(val)
        elif kw == "component":
            components.update(val)
        elif kw == "model_selector":
            model_selectors.update(val)
        else:
            kw_dict.update({kw: val})

    kw_dict.update(
        {
            "components": components,
            "models": models,
            "model_selectors": model_selectors,
        }
    )

    validate_ibis_model(kw_dict)
    return kw_dict


def parse_ibis_file(ibis_file: str | Path) -> dict:
    """Parse the contents of an IBIS file.

    Args:
        ibis_file (str | Path): The name of the IBIS file.
    Example:
        >>> model_dict = parse_ibis_file(ibis_file)
    Returns:
        model_dict: Dictionary containing keyword definitions (empty upon failure).
    """
    with open(Path(ibis_file), "r", encoding="utf-8") as file:
        return parse_ibis_string(file.read())


def validate_ibis_model(model_dict):
    """Validate the IBIS model has all the required keywords for a PyBERT simulation to run."""
    logger.debug("Validating IBIS model:\n%s", model_dict)
    if not model_dict["components"]:
        raise MalformedIBISFileError("This IBIS model has no components!")
    if not model_dict["models"]:
        raise MalformedIBISFileError("This IBIS model has no models!")

    for model in model_dict["models"].values():
        if model["model_type"] is None:
            raise MalformedIBISFileError("This IBIS model has no model type!")
            if model["model_type"].lower() in ("output", "i/o"):
                if "pulldown" not in model or "pullup" not in model:
                    raise MalformedIBISFileError("This IBIS model has no I-V curves!")
                if "ramp" not in model:
                    raise MalformedIBISFileError("This IBIS model has no ramp values!")
            elif model["model_type"].lower() in ("input"):
                if "gnd_clamp" not in model or "power_clamp" not in model:
                    raise MalformedIBISFileError("This IBIS model has no clamp values!")
        if model["voltage_range"] is None:
            raise MalformedIBISFileError("This IBIS model has no voltage range!")
    return model_dict
