"""Classes for encapsulating IBIS model constituents.

Original Author: David Banas <capn.freako@gmail.com>

Original Date:   November 1, 2019

For information regarding the IBIS modeling standard, visit:
https://ibis.org/

Copyright (c) 2019 by David Banas; All rights reserved World wide.
"""

import platform
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from pyibisami.ibis.gui import IBISModelView


@dataclass
class Pin:
    name: str = ""
    model_name: str = ""
    rlc_pin: tuple[float, float, float] = (0.0, 0.0, 0.0)

    @classmethod
    def from_tuple(cls, name: str, pin: tuple[str, tuple[float, float, float]]):
        return cls(
            name=name,
            model_name=pin[0],
            rlc_pin=pin[1],
        )


@dataclass
class Package:
    resistance: float = 0.0
    capacitance: float = 0.0
    inductance: float = 0.0

    def __str__(self):
        return f"r_pkg={self.resistance}, c_pkg={self.capacitance}, l_pkg={self.inductance}"


@dataclass
class Component:
    """Encapsulation of a particular component from an IBIS model file."""

    name: str
    manufacturer: str
    package: Package
    pins: Dict[str, Any] = field(default_factory=dict)
    diff_pins: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, name: str, component: dict):
        return cls(
            name=name,
            manufacturer=component.get("manufacturer", ""),
            package=Package(
                resistance=component.get("package", {}).get("r_pkg", 0.0),
                capacitance=component.get("package", {}).get("c_pkg", 0.0),
                inductance=component.get("package", {}).get("l_pkg", 0.0),
            ),
            # pins=component.get("pin", {}),
            pins={name: Pin.from_tuple(name, pin) for name, pin in component.get("pin", {}).items()},
            diff_pins=component.get("diff_pin", {}),
        )


@dataclass
class Model:
    """Encapsulation of a particular I/O model from an IBIS model file.

    Depending on the model type, some of the attributes may be None since only some are required
    depending on the which ones are set.
    """

    name: str
    model_type: str
    voltage_range: Tuple[float, float]
    c_comp: Optional[float] = None
    cref: Optional[float] = None
    vref: Optional[float] = None
    vmeas: Optional[float] = None
    rref: Optional[float] = None
    temperature_range: Optional[Tuple[float, float]] = None
    ramp: Optional[dict] = None
    algorithmic_model: Optional[dict] = None
    pulldown: Optional[list] = None
    pullup: Optional[list] = None
    gnd_clamp: Optional[list] = None
    power_clamp: Optional[list] = None
    _impedance: Optional[float] = field(init=False, default=None)
    _slew: Optional[float] = field(init=False, default=None)
    _plot_data: dict = field(init=False, default_factory=dict)
    _ami_file: Optional[Path] = field(init=False, default=None)
    _dll_file: Optional[Path] = field(init=False, default=None)

    def __post_init__(self):
        self._plot_data = self.__process_model()
        self._ami_file, self._dll_file = self.get_algorithmic_model_for_operating_system(self.algorithmic_model)

    @classmethod
    def from_dict(cls, name: str, model: dict):
        return cls(
            name=name,
            model_type=model.get("model_type", ""),
            voltage_range=model.get("voltage_range", (0.0, 0.0)),
            c_comp=model.get("c_comp", None),
            cref=model.get("cref", None),
            vref=model.get("vref", None),
            vmeas=model.get("vmeas", None),
            rref=model.get("rref", None),
            temperature_range=model.get("temperature_range", None),
            ramp=model.get("ramp", None),
            algorithmic_model=model.get("algorithmic_model", None),
            pulldown=model.get("pulldown", None),
            pullup=model.get("pullup", None),
            gnd_clamp=model.get("gnd_clamp", None),
            power_clamp=model.get("power_clamp", None),
        )

    def gui(self):
        gui = IBISModelView(self)
        gui.exec()

    def __process_model(self):
        # Infer impedance and/or rise/fall time, as per model type.
        mtype = self.model_type.lower()
        plotdata = {}
        if mtype in ("output", "i/o"):
            pd_vs, pd_ityps, pd_imins, pd_imaxs, pd_zs = self.proc_iv(self.pulldown, self.vmeas)
            pu_vs, pu_ityps, pu_imins, pu_imaxs, pu_zs = self.proc_iv(self.pullup, self.vmeas)
            pu_vs = self.voltage_range[0] - np.array(pu_vs)  # Correct for Vdd-relative pull-up voltages.
            pu_ityps = -np.array(pu_ityps)  # Correct for current sense, for nicer plot.
            pu_imins = -np.array(pu_imins)
            pu_imaxs = -np.array(pu_imaxs)
            self._impedance = (list(pd_zs)[0] + list(pu_zs)[0]) / 2
            plotdata["pd_vs"] = pd_vs
            plotdata["pd_ityps"] = pd_ityps
            plotdata["pd_imins"] = pd_imins
            plotdata["pd_imaxs"] = pd_imaxs
            plotdata["pu_vs"] = pu_vs
            plotdata["pu_ityps"] = pu_ityps
            plotdata["pu_imins"] = pu_imins
            plotdata["pu_imaxs"] = pu_imaxs

            self._slew = (self.ramp["rising"][0] + self.ramp["falling"][0]) / 2e9  # (V/ns)
        elif mtype == "input":

            if self.gnd_clamp:
                gc_vs, gc_ityps, gc_imins, gc_imaxs, gc_zs = self.proc_iv(self.gnd_clamp, self.vmeas)
                gc_z = list(gc_zs)[0]  # Use typical value for Zin calc.
                plotdata.update({"gc_vs": gc_vs, "gc_ityps": gc_ityps, "gc_imins": gc_imins, "gc_imaxs": gc_imaxs})

            if self.power_clamp:
                pc_vs, pc_ityps, pc_imins, pc_imaxs, pc_zs = self.proc_iv(self.power_clamp, self.vmeas)
                pc_z = list(pc_zs)[0]
                pc_vs = self.voltage_range[0] - np.array(pc_vs)  # Correct for Vdd-relative pull-up voltages.
                pc_ityps = -np.array(pc_ityps)  # Correct for current sense, for nicer plot.
                pc_imins = -np.array(pc_imins)
                pc_imaxs = -np.array(pc_imaxs)
                plotdata.update({"pc_vs": pc_vs, "pc_ityps": pc_ityps, "pc_imins": pc_imins, "pc_imaxs": pc_imaxs})

            if self.gnd_clamp and self.power_clamp:
                # Parallel combination, as both clamps are always active.
                self._impedance = (gc_z * pc_z) / (gc_z + pc_z)  # pylint: disable=possibly-used-before-assignment
            elif self.gnd_clamp:
                self._impedance = gc_z
            else:
                self._impedance = pc_z

        return plotdata

    @property
    def impedance(self):
        """The impedance of the I/O model."""
        return self._impedance

    @property
    def slew(self):
        """The driver slew rate."""
        return self._slew

    @property
    def ccomp(self):
        """The parasitic capacitance."""
        return self.c_comp

    @property
    def mtype(self):
        """Model type."""
        return self.model_type

    @property
    def plot_data(self):
        """The plot data for the model."""
        return self._plot_data

    @property
    def ami_file(self):
        """If there was an ami file for this model and it matches the current operating system, return it."""
        return self._ami_file

    @property
    def dll_file(self):
        """If there was a dll file for this model and it matches the current operating system, return it."""
        return self._dll_file

    @staticmethod
    def get_algorithmic_model_for_operating_system(algorithmic_model: dict[str, list[str]]) -> tuple[str, str]:
        """Based off the operating system, return the appropriate algorithmic model and DLL/SO and AMI file as Path objects."""

        if algorithmic_model:
            os_name = platform.system().lower()  # 'windows', 'linux', etc.
            if os_name.startswith("win"):
                os_key = "windows"
            elif os_name.startswith("lin"):
                os_key = "linux"
            else:
                # Not supported
                return None, None

            # Detect architecture
            arch = "64" if sys.maxsize > 2**32 else "32"

            # The keys in algorithmic_model are like ('windows', '64'), etc.
            for os_arch, files in algorithmic_model:
                if isinstance(os_arch, tuple) and len(os_arch) == 2:
                    os_val, arch_val = os_arch
                    if os_val.lower() == os_key and str(arch_val) == arch:
                        # files should be [dll/so, ami]
                        if len(files) == 2:
                            return files[0], files[1]
        return None, None

    @staticmethod
    def proc_iv(xs, v_measure):
        """Process an I/V table."""
        if len(xs) < 2:
            raise ValueError("Insufficient number of I-V data points!")
        try:
            vs, iss = zip(*(xs))  # Idiomatic Python for ``unzip``.
        except Exception as exc:
            raise ValueError(f"xs: {xs}") from exc
        ityps, imins, imaxs = zip(*iss)

        def calcZ(x):
            (vs, ivals) = x
            if v_measure:
                ix = np.where(np.array(vs) >= v_measure)[0][0]
            else:
                ix = np.where(np.array(vs) >= max(vs) / 2)[0][0]
            try:
                return abs((vs[ix] - vs[ix - 1]) / (ivals[ix] - ivals[ix - 1]))
            except ZeroDivisionError:
                return 1e7  # Use 10 MOhms in place of infinity.

        zs = map(calcZ, zip([vs, vs, vs], [ityps, imins, imaxs]))
        return vs, ityps, imins, imaxs, zs
