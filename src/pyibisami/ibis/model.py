"""A class for encapsulating IBIS model files.

Original Author: David Banas <capn.freako@gmail.com>

Original Date:   November 1, 2019

For information regarding the IBIS modeling standard, visit:
https://ibis.org/

Copyright (c) 2019 by David Banas; All rights reserved World wide.
"""

import logging
from pathlib import Path

from pyibisami.ibis.gui import IBISModelSelector
from pyibisami.ibis.items import Component, Model, Pin
from pyibisami.ibis.parser import parse_ibis_file, parse_ibis_string

logger = logging.getLogger("pyibisami.ibis")


class IBISModel:
    """Dataclass for wrapping and interacting with an IBIS model.

    This class can be configured to present a customized GUI to the user
    for interacting with a particular IBIS model (i.e. - selecting components,
    pins, and models).

    The intended use of this class is as follows:

     1. Instantiate this class only once per IBIS model file.
        When instantiating from one of the class methods, you can provide either the unprocessed
        contents of the IBIS file, as a single string, or the string path of the IBIS file.
        Those methods will take care of getting it parsed and log any errors or warnings.

     2. When you want to let the user select a particular component/pin/model,
        open the GUI by calling the ``gui()`` method.

    Args:
        name (str): The name of the IBIS model.
        filepath (Path): The path to the IBIS file.
        is_tx (bool): True if this is a Tx model.
        version (float): The version of the IBIS file.
        revision (str): The revision of the IBIS file.
        date (str): The date of the IBIS file.
        components (dict): The dictionary of components in the IBIS file.
        models (dict): The dictionary of models in the IBIS file.
        model_selectors (dict): The dictionary of model selectors in the IBIS file.
    """

    # pylint: disable=too-many-instance-attributes, too-many-arguments, too-many-positional-arguments

    def __init__(
        self,
        filepath: Path,
        is_tx: bool,
        version: float,
        revision: str,
        date: str,
        components: dict[str, Component],
        models: dict[str, Model],
        model_selectors: dict[str, list[str]],
        name: str | None = None,
    ):
        self.name: str = name or filepath.stem
        self.filepath: Path = filepath
        self.is_tx: bool = is_tx
        self.version: float = version
        self.revision: str = revision
        self.date: str = date

        # The dictionary of components and models in the IBIS file.
        self.components: dict[str, Component] = components
        self._current_component: str = next(iter(self.components))

        self.pins: dict[str, Pin] = self.components[self._current_component].pins
        self._current_pin: str = next(iter(self.pins))

        self.models: dict[str, Model] = models
        self.model_selectors: dict[str, list[str]] = model_selectors
        self._current_model: str = self.get_models(self.current_pin.model_name)[0]

    @classmethod
    def from_file(cls, filepath: str | Path, is_tx: bool):
        """Initialize the IBISModel from a file.

        Args:
            filename (str): The string path of the IBIS file.
            is_tx (bool): True if this is a Tx model.
        """
        filepath = Path(filepath)
        logger.info("IBISModel initializing from %s...", filepath)
        model_dict = parse_ibis_file(filepath)  # Parse the IBIS file contents and validate it.
        instance = cls(
            filepath=filepath,
            is_tx=is_tx,
            version=float(model_dict["ibis_ver"]),
            revision=model_dict["file_rev"],
            date=model_dict["date"],
            components={
                name: Component.from_dict(name, component) for name, component in model_dict["components"].items()
            },
            models={name: Model.from_dict(name, model) for name, model in model_dict["models"].items()},
            model_selectors=model_dict.get("model_selectors", {}),
            name=model_dict["file_name"],
        )
        logger.debug("Finished initializing IBISModel.")
        return instance

    @classmethod
    def from_string(cls, ibis_string: str, is_tx: bool):
        """Initialize the IBISModel from a string.

        Args:
            ibis_string (str): The unprocessed contents of the IBIS file.
            is_tx (bool): True if this is a Tx model.
        """
        model_dict = parse_ibis_string(ibis_string)  # Parse the IBIS file contents and validate it.
        return cls(
            filepath=Path(model_dict["file_name"]),  # Name will also be set to file_name
            is_tx=is_tx,
            version=float(model_dict["ibis_ver"]),
            revision=model_dict["file_rev"],
            date=model_dict["date"],
            components={
                name: Component.from_dict(name, component) for name, component in model_dict["components"].items()
            },
            models={name: Model.from_dict(name, model) for name, model in model_dict["models"].items()},
            model_selectors=model_dict.get("model_selectors", {}),
        )

    @classmethod
    def from_dict(cls, model_dict: dict, is_tx: bool):
        """Initialize the IBISModel from a dictionary.

        Args:
            model_dict (dict): The dictionary of model information.
            is_tx (bool): True if this is a Tx model.
        """
        return cls(
            filepath=Path(model_dict["file_name"]),  # Name will also be set to file_name
            is_tx=is_tx,
            version=float(model_dict["ibis_ver"]),
            revision=model_dict["file_rev"],
            date=model_dict["date"],
            components={
                name: Component.from_dict(name, component) for name, component in model_dict["components"].items()
            },
            models={name: Model.from_dict(name, model) for name, model in model_dict["models"].items()},
            model_selectors=model_dict.get("model_selectors", {}),
        )

    def get_models(self, model_name: str) -> list[str]:
        """Return the list of models associated with a particular name.

        IBIS models can either directly assign a model name in the pin definition or it can reference a model
        selector which allows a pin to have multiple options for the model.

        Args:
            model_name (str): The name of the model to get the list of models for.

        Returns:
            list[str]: The list of models associated with the model name.

        """
        if self.model_selectors and model_name in self.model_selectors:
            return [model[0] for model in self.model_selectors[model_name]]  # There was a model selector
        return [model_name]  # The pin directly references a model

    def get_pins(self):
        """Get the list of appropriate pins, given our type (i.e. - Tx or Rx).

        Returns:
            list[str]: List of pin names that match the model type (Tx or Rx)
        """
        valid_pins = []
        for pin in self.current_component.pins.values():
            # Get all possible models for this pin
            model_names = self.get_models(pin.model_name)
            model = self.models[
                model_names[0]
            ]  # Get first model to check type; can assume all models are the same type

            # Check if model type matches is_tx flag
            model_type = model.model_type.lower()
            if self.is_tx:
                if model_type in ("output", "i/o"):
                    valid_pins.append(pin.name)
            else:
                valid_pins.append(pin.name)

        return valid_pins

    def gui(self, get_handle: bool = False) -> IBISModelSelector | None:
        """Present a customized GUI to the user, for model selection, etc."""
        gui = IBISModelSelector(self)

        if get_handle:  # Used for testing so we can get the handle to the GUI without opening the Dialog.
            return gui

        gui.exec()
        return None

    @property
    def current_component(self) -> Component:
        """Return the current component object."""
        return self.components[self._current_component]

    @current_component.setter
    def current_component(self, value: str):
        """Set the current component and update the pins and current pin to the first pin in the component."""
        self._current_component = value
        self.pins = self.current_component.pins
        self.current_pin = next(iter(self.pins))

    @property
    def current_model(self) -> Model:
        """Return the current model object."""
        return self.models[self._current_model]

    @current_model.setter
    def current_model(self, value: str):
        """Set the current model"""
        if value not in self.models:
            raise ValueError(f"Model {value} not found in models")
        self._current_model = value

    @property
    def current_pin(self) -> Pin:
        """Return the current pin object."""
        return self.pins[self._current_pin]

    @current_pin.setter
    def current_pin(self, value: str):
        """Set the current pin and update the current model to the first model in the pin."""
        self._current_pin = value
        self.current_model = self.get_models(self.current_pin.model_name)[0]

    @property
    def ami_file(self) -> Path:
        """Return the AMI file path.

        AMI files are relative to the ibis file in the .ibs definition.  Join with the parent directory of the ibis file.
        """
        if self.current_model.ami_file:
            return self.filepath.parent / self.current_model.ami_file
        return None

    @property
    def dll_file(self) -> Path:
        """Return the DLL file path.

        DLL files are relative to the ibis file in the .ibs definition.  Join with the parent directory of the ibis file.
        """
        if self.current_model.dll_file:
            return self.filepath.parent / self.current_model.dll_file
        return None

    @property
    def has_algorithmic_model(self) -> bool:
        """Return True if the model has an algorithmic model."""
        return True if self.current_model.ami_file and self.current_model.dll_file else False

    @property
    def pin_rlcs(self) -> tuple[float, float, float]:
        """Return the RLC values for the pin, if the values are 0, return the package RLC values."""
        pin_rlc = self.current_pin.rlc_pin
        if all(val == 0 for val in pin_rlc.values()):
            return self.current_component.pkg_rlc
        return pin_rlc
