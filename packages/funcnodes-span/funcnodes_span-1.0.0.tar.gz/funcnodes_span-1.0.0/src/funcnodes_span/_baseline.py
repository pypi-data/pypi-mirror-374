from typing import Tuple, Optional
import numpy as np
from scipy.ndimage import gaussian_filter1d
from ._curves import knee_point_detection, outlier_detection_std


def estimate_baseline_regions(
    x: np.ndarray,
    y: np.ndarray,
    pre_flatted_y: Optional[np.ndarray] = None,
    window: Optional[float] = None,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Estimate the baseline regions of a curve.

    Parameters
    ----------
    x : np.ndarray
        The x values of the curve.
    y : np.ndarray
        The y values of the curve.
    pre_flatted_y : np.ndarray, optional
        The y values of the curve when flattet.
    window : float, optional
        The window size for the gaussian filter.relative to the x values. Default is 1% of the x values.

    Returns
    -------
    y_bl : np.ndarray
        The baseline of the curve, linearly interpolated between the baseline regions.
    is_baseline_region : np.ndarray
        A boolean array indicating the baseline region.
    """

    if window is None:
        window = len(y) / 100  # default value as absolute number of points
    else:
        # if window is a float, the number of points is calculated as as if window is in x units
        window = int(window / (np.median(np.diff(x)) if x is not None else 1) + 0.5)

    window = max(1, window)

    if pre_flatted_y is None:
        pre_flatted_y = y

    smoothed_baseline_corrected_y = gaussian_filter1d(pre_flatted_y, window)

    percentage_cutoff = np.arange(0, 1, 0.0001)

    abs_smoothed_baseline_corrected_y = (
        smoothed_baseline_corrected_y + smoothed_baseline_corrected_y.min()
    )

    norm_smoothed_y = abs_smoothed_baseline_corrected_y / np.max(
        abs_smoothed_baseline_corrected_y
    )

    norm_y = np.abs(pre_flatted_y)
    norm_y = norm_y / np.max(norm_y)

    cumulative_n_points = np.sum(norm_smoothed_y[:, None] < percentage_cutoff, axis=0)
    cumulative_n_points = cumulative_n_points / np.max(cumulative_n_points)

    elbow_idx, elbow_x, elbow_y = knee_point_detection(
        percentage_cutoff, cumulative_n_points
    )

    is_baseline_region = norm_y <= elbow_x

    outliers = outlier_detection_std(
        x[is_baseline_region],
        norm_y[is_baseline_region],
        threshold=3,
        max_iterations=9,
    )

    is_baseline_region[is_baseline_region] &= ~outliers

    is_baseline_region = is_baseline_region.astype(float)

    smoothed_is_baseline_region = gaussian_filter1d(is_baseline_region, window)
    smoothed_is_baseline_region = (
        smoothed_is_baseline_region >= 0.99 * smoothed_is_baseline_region.max()
    )

    if np.any(smoothed_is_baseline_region):
        y_bl = np.interp(
            x, x[smoothed_is_baseline_region], y[smoothed_is_baseline_region]
        )
    else:
        y_bl = np.zeros_like(y)

    return y_bl, smoothed_is_baseline_region
