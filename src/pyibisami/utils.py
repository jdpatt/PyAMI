"""Utility functions for pyibisami."""

import builtins
import logging
from typing import Any

import numpy as np
from scipy.linalg import convolution_matrix, lstsq

from pyibisami.common import Rvec

logger = logging.getLogger(__name__)


def setattr(obj: object, name: str, value: Any, /) -> None:
    """Wrapper around builtins.setattr to log the changes from the GUI.

    You can patch setattr in the gui module to see the changes as they are made.

    Example:
        ```python
        from pyibisami.utils import setattr
        import pyibisami.ibis.gui
        pyibisami.ibis.gui.setattr = setattr
        ```
    """
    # pylint: disable=redefined-builtin
    builtins.setattr(obj, name, value)
    logger.debug("Set %s to %s", name, value)


def deconv_same(y: Rvec, x: Rvec) -> Rvec:
    """Deconvolve input from output, to recover filter response, for same length I/O.

    Args:
        y: output signal
        x: input signal

    Returns:
        h: filter impulse response.
    """
    A = convolution_matrix(x, len(y), "same")
    h, _, _, _ = lstsq(A, y)
    return h


def loadWave(filename: str) -> tuple[Rvec, Rvec]:
    """Load a waveform file.

    The file should consist of any number of lines, where each line
    contains, first, a time value and, second, a voltage value.
    Assume the first line is a header, and discard it.

    Specifically, this function may be used to load in waveform files
    saved from *CosmosScope*.

    Args:
        filename: Name of waveform file to read in.

    Returns:
        A pair of *NumPy* arrays containing the time and voltage values, respectively.
    """

    with open(filename, "r", encoding="utf-8") as theFile:
        theFile.readline()  # Consume the header line.
        time = []
        voltage = []
        for line in theFile:
            tmp = list(map(float, line.split()))
            time.append(tmp[0])
            voltage.append(tmp[1])
        return (np.array(time), np.array(voltage))


def interpFile(filename: str, sample_per: float) -> Rvec:
    """Read in a waveform from a file, and convert it to the given sample rate, using linear interpolation.

    Args:
        filename: Name of waveform file to read in.
        sample_per: New sample interval, in seconds.

    Returns:
        A *NumPy* array containing the resampled waveform.
    """

    impulse = loadWave(filename)
    ts = impulse[0]
    ts = ts - ts[0]
    vs = impulse[1]
    tmax = ts[-1]
    # Build new impulse response, at new sampling period, using linear interpolation.
    res = []
    t = 0.0
    i = 0
    while t < tmax:
        while ts[i] <= t:
            i = i + 1
        res.append(vs[i - 1] + (vs[i] - vs[i - 1]) * (t - ts[i - 1]) / (ts[i] - ts[i - 1]))
        t = t + sample_per
    return np.array(res)
