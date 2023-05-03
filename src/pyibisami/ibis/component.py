"""Classes for encapsulating IBIS model constituents.

Original Author: David Banas <capn.freako@gmail.com>

Original Date:   November 1, 2019

For information regarding the IBIS modeling standard, visit:
https://ibis.org/

Copyright (c) 2019 by David Banas; All rights reserved World wide.
"""
from dataclasses import dataclass, field

from pyibisami.ibis.package import Package
from pyibisami.ibis.pin import Pin


@dataclass
class Component:
    """Encapsulation of a particular component from an IBIS model file."""

    name: str = ""
    manufacturer: str = ""
    package: Package = Package()
    _pins: dict[str, Pin] = field(default_factory=dict)
    _selected_pin: str = ""

    def get_current_pin(self) -> Pin:
        return self.pins[self._selected_pin]

    def set_current_pin(self, pin_name):
        if pin_name in self.pins.keys():
            self._selected_pin = pin_name

    @property
    def pins(self):
        "The names of all pins supported by this component."
        return list(self._pins.keys())

    def add_pin(self, pin: Pin):
        self._pins.update({pin.name, pin})
