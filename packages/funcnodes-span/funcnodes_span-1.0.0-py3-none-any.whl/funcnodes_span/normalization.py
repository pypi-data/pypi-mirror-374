from typing import Literal, Tuple
from funcnodes import NodeDecorator, Shelf
import numpy as np
from scipy.interpolate import interp1d
from exposedfunctionality import controlled_wrapper
import funcnodes as fn


class NormMode(fn.DataEnum):
    ZERO_ONE = "zero_one"
    MINUS_ONE_ONE = "minus_one_one"
    SUM_ABS = "sum_abs"
    SUM = "sum"
    EUCLIDEAN = "euclidean"
    MEAN_STD = "mean_std"
    MAX = "max"


@NodeDecorator(id="span.basics.norm", name="Normalization node")
def _norm(array: np.ndarray, mode: NormMode = NormMode.ZERO_ONE) -> np.ndarray:
    # """
    # Apply different normalizations to the array.

    # Args:
    #     array (np.ndarray): The input array to be normalized.
    #     mode (NormMode): The normalization mode to apply. Defaults to NormMode.ZERO_ONE.

    # Returns:
    #     np.ndarray: The normalized array.

    # Raises:
    #     ValueError: If an unsupported normalization mode is provided.
    # """
    mode = NormMode.v(mode)
    normalization_methods = {
        NormMode.ZERO_ONE.value: lambda x: (x - np.amin(x)) / (np.amax(x) - np.amin(x)),
        NormMode.MINUS_ONE_ONE.value: lambda x: 2
        * ((x - np.amin(x)) / (np.amax(x) - np.amin(x)))
        - 1,
        NormMode.SUM_ABS.value: lambda x: x / np.abs(x).sum(),
        NormMode.SUM.value: lambda x: x / x.sum(),
        NormMode.EUCLIDEAN.value: lambda x: x / np.sqrt((x**2).sum()),
        NormMode.MEAN_STD.value: lambda x: (x - x.mean()) / x.std(),
        NormMode.MAX.value: lambda x: x / x.max(),
    }
    if mode not in normalization_methods.keys():
        raise ValueError(f"Unsupported normalization mode: {mode}")
    return normalization_methods[mode](array)


def density_normalization(
    x: np.ndarray,
    y: np.ndarray,
    num_points: int = None,
    distance_estimation: Literal["median", "mean", "min", "max"] = "median",
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Redistributes the x and y coordinates to have evenly spaced x-values while retaining original points.

    Parameters:
        x (np.ndarray): Uneven, unsorted x coordinates.
        y (np.ndarray): Corresponding y values.
        num_points (int, optional): Total number of points in the final grid.
                                    Must be greater than or equal to the number of unique original x values.
                                    If None, it is estimated based on the specified distance estimation method.
        distance_estimation (Literal["median", "mean", "min", "max"], optional):
            Method to estimate the spacing between points when num_points is not provided.
            Options include "median", "mean", "min", "max". Defaults to "median".

    Returns:
        Tuple[np.ndarray, np.ndarray]:
            - x_new: Evenly spaced x coordinates including original x points.
            - y_new: Corresponding interpolated y values."""
    # Convert inputs to numpy arrays
    x = np.array(x)
    y = np.array(y)

    # if x is already evenly spaced, return the input
    if len(np.unique(np.diff(x))) == 1:
        return x, y

    # Sort the data based on x values
    sorted_indices = np.argsort(x)
    x_sorted = x[sorted_indices]
    y_sorted = y[sorted_indices]

    # Handle duplicate x-values by averaging their y-values
    unique_x, indices, counts = np.unique(
        x_sorted, return_index=True, return_counts=True
    )
    y_unique = np.array([y_sorted[i : i + c].mean() for i, c in zip(indices, counts)])

    # Determine number of points for the evenly spaced grid

    if num_points is None:
        distance_func = {
            "mean": np.mean,
            "median": np.median,
            "min": np.min,
            "max": np.max,
        }.get(distance_estimation, np.median)  # Default to median if key not found

        unique_diffs = np.diff(unique_x)

        # Handle the case where there is only one unique_x point
        if len(unique_diffs) == 0:
            num_points = 1
        else:
            estimated_diff = distance_func(unique_diffs)
            total_range = unique_x.max() - unique_x.min()

            # Prevent division by zero
            if estimated_diff == 0:
                num_points = len(unique_x)
            else:
                num_points = int(total_range / estimated_diff)
    else:
        num_points = int(num_points)
    # Create evenly spaced x-values
    x_new = np.linspace(unique_x.min(), unique_x.max(), num_points)

    # Create an interpolation function
    interp_func = interp1d(unique_x, y_unique, kind="linear", fill_value="extrapolate")

    # Compute the interpolated y-values
    y_new = interp_func(x_new)

    return x_new, y_new


@NodeDecorator(
    id="span.norm.density",
    name="Density normalization node",
    description="Redistributes the x and y coordinates to have evenly spaced x-values while retaining original points.",
    outputs=[
        {
            "name": "x_new",
            "description": "Evenly spaced x coordinates including original x points.",
        },
        {
            "name": "y_new",
            "description": "Corresponding interpolated y values.",
        },
    ],
)
@controlled_wrapper(density_normalization, wrapper_attribute="__fnwrapped__")
def density_normalization_node(
    x: np.ndarray,
    y: np.ndarray,
    num_points: int = None,
    distance_estimation: Literal["median", "mean", "min", "max"] = "median",
) -> Tuple[np.ndarray, np.ndarray]:
    return density_normalization(x, y, num_points, distance_estimation)


NORM_NODE_SHELF = Shelf(
    nodes=[_norm, density_normalization_node],
    subshelves=[],
    name="Normalization",
    description="Normalization of the spectra",
)
