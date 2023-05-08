"""A class for encapsulating IBIS model files.

Original Author: David Banas <capn.freako@gmail.com>

Original Date:   November 1, 2019

For information regarding the IBIS modeling standard, visit:
https://ibis.org/

*Note:* The ``IBISModel`` class, defined here, needs to be kept separate from the
other IBIS-related classes, defined in the ``ibis_model`` module, in order to
avoid circular imports.

Copyright (c) 2019 by David Banas; All rights reserved World wide.
"""
import logging
from pathlib import Path
from typing import Optional, Union

from pyibisami.ibis.buffer_model import BufferModel
from pyibisami.ibis.component import Component
from pyibisami.ibis.parser import parse_file_into_model

logger = logging.getLogger(__name__)


class IBISModel:
    """

    Args:
        filepath: The filepath of where the IBIS file lives.
        components: The parsed components in the file.
        models: The parsed models in the file.
        filename: The filename from the ibis file or the stem of the filepath
        ibis_version: Which version of the ibis specification is this model.
    """

    def __init__(
        self,
        filepath: Union[str, Path],
        components: dict[str, Component],
        models: dict[str, BufferModel],
        filename: str = "",
        ibis_version: float = 0.0,
    ):
        self.filepath = Path(filepath)
        self.filename = filename or self.filepath.stem
        self.ibis_version: float = ibis_version

        self.components: dict[str, Component] = components
        self.models: dict[str, BufferModel] = models

        self.selected_component: Optional[Component] = None
        self.selected_model: Optional[BufferModel] = None

    @classmethod
    def from_ibis_file(cls, filepath: Union[str, Path]):
        """Parse the IBIS file and get all of the high level information from it.

        We don't need to parse everything and validate it all at the beginning but defer that to when a simulation
        runs.  Not all models may be used and as long as the one we need validates, the simulation can proceed.
        """
        with open(filepath, "r", encoding="utf-8") as file:
            return parse_file_into_model(file.read(), cls(filepath))

    def __str__(self):
        return f"IBIS Model '{self.filename}'"
