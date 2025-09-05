from typing import Dict, Callable, Union
from funcnodes import NodeDecorator, Shelf
import numpy as np
import pandas as pd
from scipy.signal import savgol_filter, medfilt
from scipy.ndimage import gaussian_filter1d
import warnings
import funcnodes as fn

warnings.filterwarnings("ignore")


class SmoothMode(fn.DataEnum):
    SAVITZKY_GOLAY = "savgol"
    GAUSSIAN = "gaussian"
    MOVING_AVERAGE = "ma"
    EXPONENTIAL_MOVING_AVERAGE = "ema"
    MEDIAN = "median"


def smooth_savgol(x: np.ndarray, window: int) -> np.ndarray:
    return savgol_filter(x, window, 2)


def smooth_gaussian(x: np.ndarray, window: int) -> np.ndarray:
    return gaussian_filter1d(x, window)


def smooth_ma(x: np.ndarray, window: int) -> np.ndarray:
    if x.ndim > 1:
        n, m = x.shape
        result = np.zeros((n, m))
        for i in range(n):
            result[i, :] = np.convolve(x[i, :], np.ones(window) / window, mode="same")
        return result
    else:
        return np.convolve(x, np.ones(window) / window, mode="same")


def smooth_ema(x: np.ndarray, window: int) -> np.ndarray:
    if x.ndim > 1:
        n, m = x.shape
        result = np.zeros((n, m))
        for i in range(n):
            result[i, :] = pd.Series(x[i, :]).ewm(span=window).mean().values
        return result
    else:
        return pd.Series(x).ewm(span=window).mean().values


def smooth_median(x: np.ndarray, window: int) -> np.ndarray:
    return medfilt(x, window)


_SMOOTHING_MAPPER: Dict[str, Callable[[np.ndarray, int], np.ndarray]] = {
    SmoothMode.SAVITZKY_GOLAY.value: smooth_savgol,
    SmoothMode.GAUSSIAN.value: smooth_gaussian,
    SmoothMode.MOVING_AVERAGE.value: smooth_ma,
    SmoothMode.EXPONENTIAL_MOVING_AVERAGE.value: smooth_ema,
    SmoothMode.MEDIAN.value: smooth_median,
}


@NodeDecorator(
    "span.basics.smooth",
    name="Smoothing",
    outputs=[{"name": "smoothed"}],
)
def _smooth(
    y: np.ndarray,
    mode: SmoothMode = SmoothMode.SAVITZKY_GOLAY,
    window: Union[float, int] = 5,
    x: np.ndarray = None,
) -> np.ndarray:
    # """
    # Apply different smoothing techniques to the input array.
    # the window is the number of points to consider for the smoothing.
    # If x is provided, the window is in x units and is converted to points using the median x difference.

    # Args:
    #     y (np.ndarray): The input array to be smoothed.
    #     mode (SmoothMode): The smoothing mode to apply. Defaults to SmoothMode.SAVITZKY_GOLAY.
    #     window (int): The window size for the smoothing function. Defaults to 5.
    #     x (np.ndarray): The x values of the input array. Defaults to None.

    # Returns:
    #     np.ndarray: The smoothed array.

    # Raises:
    #     ValueError: If an unsupported smoothing mode is provided.
    # """
    mode = SmoothMode.v(mode)

    if mode not in _SMOOTHING_MAPPER.keys():
        raise ValueError(f"Unsupported smoothing mode: {mode}")
    y = np.asarray(y)
    if x is not None:
        x = np.asarray(x)
        med_xdiff = np.nanmedian(np.diff(x))
        window = window / med_xdiff
    window = int(window)
    if window == 0:
        return y.copy()
    return _SMOOTHING_MAPPER[mode](y, window)


# @NodeDecorator("span.basics.smooth.savgol", name="Savgol")
# def _smooth_savgol(array: np.array, window: int = 5) -> np.array:
#     """
#     Apply Savitzky-Golay smoothing to the input array.

#     Args:
#         window (int): Parameter passed to scipy.signal.savgol_filter function

#     Returns:
#         array_o (np.array): Smoothed array
#     """

#     array_o = savgol_filter(array, window, 2)

#     return array_o


# @NodeDecorator("span.basics.smooth.gaussian", name="Gaussian")
# def _smooth_gaussian(array: np.array, window: int = 5) -> np.array:
#     """
#     Apply Gaussians moothing to the input array.

#     Args:
#         window (int): Parameter passed to scipy.signal.savgol_filter function

#     Returns:
#         array_o (np.array): Smoothed array
#     """

#     array_o = gaussian_filter1d(array, window)

#     return array_o


# @NodeDecorator("span.basics.smooth.ma", name="Moving average")
# def _smooth_ma(array: np.array, window: int = 5) -> np.array:
#     """
#     Apply Moving Average moothing to the input array.

#     Args:
#         window (int): Parameter passed to scipy.signal.savgol_filter function

#     Returns:
#         array_o (np.array): Smoothed array
#     """

#     if array.ndim > 1:
#         n, m = array.shape
#         array_o = np.zeros((n, m))
#         for i in range(n):
#             array_o[i, :] = np.convolve(
#                 array[i, :], np.ones(window) / window, mode="same"
#             )
#     else:
#         array_o = np.convolve(array, np.ones(window) / window, mode="same")

#     return array_o


# @NodeDecorator(
#     "span.basics.smooth.ema", name="Exponential moving average"
# )
# def _smooth_ema(array: np.array, window: int = 5) -> np.array:
#     """
#     Apply Exponential Moving Average moothing to the input array.

#     Args:
#         window (int): Parameter passed to scipy.signal.savgol_filter function

#     Returns:
#         array_o (np.array): Smoothed array
#     """
#     if array.ndim > 1:
#         n, m = array.shape
#         array_o = np.zeros((n, m))
#         for i in range(n):
#             array_o[i, :] = pd.Series(array[i, :]).ewm(span=window).mean().values
#     else:
#         array_o = pd.Series(array).ewm(span=window).mean().values

#     return array_o


# @NodeDecorator("span.basics.smooth.median", name="Median")
# def _smooth_median(array: np.array, window: int = 5) -> np.array:
#     """
#     Apply Median smoothing to the input array.

#     Args:
#         window (int): Parameter passed to scipy.signal.savgol_filter function

#     Returns:
#         array_o (np.array): Smoothed array
#     """

#     array_o = medfilt(array, window)

#     return array_o


SMOOTH_NODE_SHELF = Shelf(
    nodes=[_smooth],
    subshelves=[],
    name="Smoothing",
    description="Smoothing of the spectra",
)
