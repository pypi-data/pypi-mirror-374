import numpy as np
from typing import Optional, Tuple


def knee_point_detection(x, y) -> Tuple[int, float, float]:
    """
    Detect the knee (or elbow) point in a curve.

    Parameters:
    x (numpy array): X-values of the curve.
    y (numpy array): Y-values of the curve.

    Returns:
    int: Index of the knee point in the input arrays.
    float: X-value of the knee point.
    float: Y-value of the knee point.

    """
    # Normalize x and y to have values between 0 and 1
    x_normalized = (x - np.min(x)) / (np.max(x) - np.min(x))
    y_normalized = (y - np.min(y)) / (np.max(y) - np.min(y))

    # Line connecting the first and last points
    line_vec = np.array(
        [x_normalized[-1] - x_normalized[0], y_normalized[-1] - y_normalized[0]]
    )
    line_vec_norm = np.sqrt(
        line_vec[0] ** 2 + line_vec[1] ** 2
    )  # Length of the line vector
    line_vec = line_vec / line_vec_norm  # Normalize the line vector

    # Calculate the distances from all points to the line
    vec_from_first = np.column_stack(
        [x_normalized - x_normalized[0], y_normalized - y_normalized[0]]
    )
    scalar_proj = np.dot(vec_from_first, line_vec)
    vec_along_line = np.outer(scalar_proj, line_vec)
    vec_to_line = vec_from_first - vec_along_line

    # Compute the distances
    distances = np.sqrt(np.sum(vec_to_line**2, axis=1))

    # Find the index of the maximum distance (knee point)
    knee_index = np.argmax(distances)

    return knee_index, x[knee_index], y[knee_index]


def estimate_noise(
    x, y, is_baseline_region: Optional[np.ndarray] = None, std_factor: float = 3
) -> float:
    """
    Estimate the noise level in a signal.
    x (numpy array): X-values of the signal.
    y (numpy array): Y-values of the signal, assumed to be baseline corrected
    baseline_region (numpy array): Boolean array indicating the baseline regions,
        here the noise will be estamated. Calcualted automatically if not provided.
    std_factor (float): Factor to multiply the standard deviation of the baseline region to estimate the noise level.
    """
    if is_baseline_region is None:
        from ._baseline import estimate_baseline_regions

        ybl, is_baseline_region = estimate_baseline_regions(x, y)
        if is_baseline_region.sum() == 0:
            raise ValueError("No baseline region found in the input data.")

    std = np.std(y[is_baseline_region])
    noise = std_factor * std
    return noise


def outlier_detection_std(
    x: np.ndarray, y: np.ndarray, threshold: float = 3, max_iterations: int = 1
) -> np.ndarray:
    """
    Detect outliers in a signal based on the standard deviation of the signal.

    Parameters:
    x (numpy array): X-values of the signal.
    y (numpy array): Y-values of the signal.
    threshold (float): Threshold for the standard deviation to detect outliers.
    max_iterations (int): Maximum number of iterations to detect outliers.

    Returns:
    numpy array: A boolean array where True indicates an outlier in the signal.
    """

    is_outlier = np.zeros_like(y, dtype=bool)
    n_outliers = 0
    for _ in range(max_iterations):
        new_outliers = y[~is_outlier]
        if new_outliers.size == 0:  # Handle the case of no non-outliers left
            break

        std = np.nanstd(new_outliers)
        mean = np.nanmean(new_outliers)
        is_outlier[~is_outlier] = np.abs(y[~is_outlier] - mean) > threshold * std

        current_outliers = is_outlier.sum()
        if current_outliers == n_outliers:
            break
        n_outliers = current_outliers

    return is_outlier
