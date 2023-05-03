# Note: The following list MUST have a complete set of keys,
#       in order for the parsing logic to work correctly!

IBIS_KEYWORDS = [
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

IBIS_NUMERICAL_SUFFIXES = {
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
