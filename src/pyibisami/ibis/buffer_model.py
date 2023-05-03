"""Classes for encapsulating IBIS model constituents.

Original Author: David Banas <capn.freako@gmail.com>

Original Date:   November 1, 2019

For information regarding the IBIS modeling standard, visit:
https://ibis.org/

Copyright (c) 2019 by David Banas; All rights reserved World wide.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class ModelType(Enum):
    INPUT = "input"
    OUTPUT = "output"
    INOUT = "i/o"


@dataclass
class RangeValue:
    """Many Model values define a typical, min and  max value."""

    typ: Optional[float]
    min: Optional[float]
    max: Optional[float]

    def value(self):
        """If we just ask for a value, always assume typical."""
        return self.typ


@dataclass
class BufferModel:
    """Encapsulation of a particular I/O model from an IBIS model file."""

    c_comp: Optional[float]
    c_ref: Optional[float]
    v_ref: Optional[float]
    r_ref: Optional[float]
    v_meas: Optional[float]
    v_range: RangeValue
    rising_ramp: RangeValue
    falling_ramp: RangeValue
    model_type: ModelType = ModelType.INPUT

    def validate(self):
        """Verify that the model has the required information so that it can be used."""
        ...

    # def proc_iv(xs):
    #     """Process an I/V table."""
    #     if len(xs) < 2:
    #         raise ValueError("Insufficient number of I-V data points!")
    #     try:
    #         vs, iss = zip(*(xs))  # Idiomatic Python for ``unzip``.
    #     except Exception as exc:
    #         raise ValueError(f"xs: {xs}") from exc
    #     ityps, imins, imaxs = zip(*iss)
    #     vmeas = self._vmeas

    #     def calcZ(x):
    #         (vs, ivals) = x
    #         if vmeas:
    #             ix = np.where(np.array(vs) >= vmeas)[0][0]
    #         else:
    #             ix = np.where(np.array(vs) >= max(vs) / 2)[0][0]
    #         try:
    #             return abs((vs[ix] - vs[ix - 1]) / (ivals[ix] - ivals[ix - 1]))
    #         except ZeroDivisionError:
    #             return 1e7  # Use 10 MOhms in place of infinity.
    #         except Exception:
    #             raise

    #     zs = map(calcZ, zip([vs, vs, vs], [ityps, imins, imaxs]))
    #     return vs, ityps, imins, imaxs, zs

    # # Infer impedance and/or rise/fall time, as per model type.
    # mtype = self._mtype.lower()
    # if mtype in ("output", "i/o"):
    #     if "pulldown" not in subDict or "pullup" not in subDict:
    #         raise LookupError("Missing I-V curves!")
    #     plotdata = ArrayPlotData()
    #     pd_vs, pd_ityps, pd_imins, pd_imaxs, pd_zs = proc_iv(subDict["pulldown"])
    #     pu_vs, pu_ityps, pu_imins, pu_imaxs, pu_zs = proc_iv(subDict["pullup"])
    #     pu_vs = self._vrange[0] - np.array(pu_vs)  # Correct for Vdd-relative pull-up voltages.
    #     pu_ityps = -np.array(pu_ityps)  # Correct for current sense, for nicer plot.
    #     pu_imins = -np.array(pu_imins)
    #     pu_imaxs = -np.array(pu_imaxs)
    #     self._zout = (list(pd_zs)[0] + list(pu_zs)[0]) / 2
    #     plotdata.set_data("pd_vs", pd_vs)
    #     plotdata.set_data("pd_ityps", pd_ityps)
    #     plotdata.set_data("pd_imins", pd_imins)
    #     plotdata.set_data("pd_imaxs", pd_imaxs)
    #     plotdata.set_data("pu_vs", pu_vs)
    #     plotdata.set_data("pu_ityps", pu_ityps)
    #     plotdata.set_data("pu_imins", pu_imins)
    #     plotdata.set_data("pu_imaxs", pu_imaxs)
    #     plot_iv = Plot(plotdata)  # , padding_left=75)
    #     # The 'line_style' trait of a LinePlot instance must be 'dash' or 'dot dash' or 'dot' or 'long dash' or 'solid'.
    #     plot_iv.plot(("pd_vs", "pd_ityps"), type="line", color="blue", line_style="solid", name="PD-Typ")
    #     plot_iv.plot(("pd_vs", "pd_imins"), type="line", color="blue", line_style="dot", name="PD-Min")
    #     plot_iv.plot(("pd_vs", "pd_imaxs"), type="line", color="blue", line_style="dash", name="PD-Max")
    #     plot_iv.plot(("pu_vs", "pu_ityps"), type="line", color="red", line_style="solid", name="PU-Typ")
    #     plot_iv.plot(("pu_vs", "pu_imins"), type="line", color="red", line_style="dot", name="PU-Min")
    #     plot_iv.plot(("pu_vs", "pu_imaxs"), type="line", color="red", line_style="dash", name="PU-Max")
    #     plot_iv.title = "Pull-Up/Down I-V Curves"
    #     plot_iv.index_axis.title = "Vout (V)"
    #     plot_iv.value_axis.title = "Iout (A)"
    #     plot_iv.index_range.low_setting = 0
    #     plot_iv.index_range.high_setting = self._vrange[0]
    #     plot_iv.value_range.low_setting = 0
    #     plot_iv.value_range.high_setting = 0.1
    #     plot_iv.legend.visible = True
    #     plot_iv.legend.align = "ul"
    #     self.plot_iv = plot_iv

    #     if not self._ramp:
    #         raise LookupError("Missing [Ramp]!")
    #     ramp = subDict["ramp"]
    #     self._slew = (ramp["rising"][0] + ramp["falling"][0]) / 2e9  # (V/ns)
    # elif mtype == "input":
    #     if "gnd_clamp" not in subDict or "power_clamp" not in subDict:
    #         raise LookupError("Missing clamp curves!")
    #     plotdata = ArrayPlotData()
    #     gc_vs, gc_ityps, gc_imins, gc_imaxs, gc_zs = proc_iv(subDict["gnd_clamp"])
    #     pc_vs, pc_ityps, pc_imins, pc_imaxs, pc_zs = proc_iv(subDict["power_clamp"])
    #     pc_vs = self._vrange[0] - np.array(pc_vs)  # Correct for Vdd-relative pull-up voltages.
    #     pc_ityps = -np.array(pc_ityps)  # Correct for current sense, for nicer plot.
    #     pc_imins = -np.array(pc_imins)
    #     pc_imaxs = -np.array(pc_imaxs)
    #     gc_z = list(gc_zs)[0]  # Use typical value for Zin calc.
    #     pc_z = list(pc_zs)[0]
    #     self._zin = (gc_z * pc_z) / (gc_z + pc_z)  # Parallel combination, as both clamps are always active.
    #     plotdata.set_data("gc_vs", gc_vs)
    #     plotdata.set_data("gc_ityps", gc_ityps)
    #     plotdata.set_data("gc_imins", gc_imins)
    #     plotdata.set_data("gc_imaxs", gc_imaxs)
    #     plotdata.set_data("pc_vs", pc_vs)
    #     plotdata.set_data("pc_ityps", pc_ityps)
    #     plotdata.set_data("pc_imins", pc_imins)
    #     plotdata.set_data("pc_imaxs", pc_imaxs)
    #     plot_iv = Plot(plotdata)  # , padding_left=75)
    #     # The 'line_style' trait of a LinePlot instance must be 'dash' or 'dot dash' or 'dot' or 'long dash' or 'solid'.
    #     plot_iv.plot(("gc_vs", "gc_ityps"), type="line", color="blue", line_style="solid", name="PD-Typ")
    #     plot_iv.plot(("gc_vs", "gc_imins"), type="line", color="blue", line_style="dot", name="PD-Min")
    #     plot_iv.plot(("gc_vs", "gc_imaxs"), type="line", color="blue", line_style="dash", name="PD-Max")
    #     plot_iv.plot(("pc_vs", "pc_ityps"), type="line", color="red", line_style="solid", name="PU-Typ")
    #     plot_iv.plot(("pc_vs", "pc_imins"), type="line", color="red", line_style="dot", name="PU-Min")
    #     plot_iv.plot(("pc_vs", "pc_imaxs"), type="line", color="red", line_style="dash", name="PU-Max")
    #     plot_iv.title = "Power/GND Clamp I-V Curves"
    #     plot_iv.index_axis.title = "Vin (V)"
    #     plot_iv.value_axis.title = "Iin (A)"
    #     plot_iv.index_range.low_setting = 0
    #     plot_iv.index_range.high_setting = self._vrange[0]
    #     plot_iv.value_range.low_setting = 0
    #     plot_iv.value_range.high_setting = 0.1
    #     plot_iv.legend.visible = True
    #     plot_iv.legend.align = "ul"
    #     self.plot_iv = plot_iv
