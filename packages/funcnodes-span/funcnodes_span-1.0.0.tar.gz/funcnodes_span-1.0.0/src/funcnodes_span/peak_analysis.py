from funcnodes import NodeDecorator, Shelf
import funcnodes as fn
from funcnodes_span._curves import estimate_noise
import numpy as np
from exposedfunctionality import controlled_wrapper
from typing import Annotated, Literal, Optional, List, Tuple
from scipy.signal import find_peaks
from scipy import signal, interpolate
from scipy.ndimage import gaussian_filter1d
from tqdm import tqdm
import copy
import plotly.graph_objs as go
from .normalization import density_normalization
from .peaks import PeakProperties

from .fitting import (
    fit_peaks,
    AUTOMODELMAP,
    fit_local_peak,
    peaks_from_fitted,
    Model,
    ModelResult,
)

# make enum from AUTOMODELMAP
AutoModelEnum = fn.DataEnum(
    "AutoModelEnum",
    AUTOMODELMAP,
)


@NodeDecorator(
    id="span.basics.peaks",
    name="Peak finder",
)
@controlled_wrapper(find_peaks, wrapper_attribute="__fnwrapped__")
def peak_finder(
    y: Annotated[
        np.ndarray,
        fn.InputMeta(
            description="Original 1D signal to analyze for peaks. If `x` is provided, must have same length."
        ),
    ],
    x: Annotated[
        Optional[np.ndarray],
        fn.InputMeta(
            description="Optional x-axis values (strictly increasing). If given, widths/distances/wlen/plateau_size are interpreted in x-units and signals are density-normalized; indices remain aligned."
        ),
    ] = None,
    on: Annotated[
        Optional[np.ndarray],
        fn.InputMeta(
            hidden=True,
            description="Optional signal to use for detection (e.g., smoothed/denoised). Measurements/centering can still use the original `y`."
        ),
    ] = None,
    index_source: Annotated[
        Literal["original", "on", "centroid"],
        fn.InputMeta(
            hidden=True,
            description="How to choose the peak center within [i,f]: 'original' uses argmax on `y`; 'on' keeps detection index; 'centroid' uses center-of-mass on `y`.",
        ),
    ] = "original",
    noise_level: Annotated[
        Optional[int],
        fn.InputMeta(
            hidden=True,
            description="Scales synthetic noise added for valley detection. Effective σ ≈ estimate_noise(x,y)/noise_level. Larger values = less added noise. Default ~5000.",
        ),
    ] = None,
    height: Annotated[
        Optional[float],
        fn.InputMeta(
            hidden=True,
            description="Minimum peak height for detection on the detection signal (`on` if given, else `y`). If None, uses `rel_height * max(detection signal)`.",
        ),
    ] = None,
    threshold: Annotated[
        Optional[float],
        fn.InputMeta(
            hidden=True,
            description="Required vertical step to neighbors for a peak (same units as detection signal). See `scipy.signal.find_peaks`.",
        ),
    ] = None,
    distance: Annotated[
        Optional[float],
        fn.InputMeta(
            hidden=True,
            description="Minimum horizontal distance between neighboring peaks. Interpreted in x-units if `x` is provided, otherwise in samples.",
        ),
    ] = None,
    prominence: Annotated[
        Optional[float],
        fn.InputMeta(
            hidden=True,
            description="Minimum required prominence of peaks, computed on the detection signal. See `scipy.signal.find_peaks`.",
        ),
    ] = None,
    width: Annotated[
        Optional[float],
        fn.InputMeta(
            hidden=True,
            description="Minimum peak width measured at `width_at_rel_height` of peak height. In x-units if `x` is provided, else in samples.",
        ),
    ] = None,
    wlen: Annotated[
        Optional[int],
        fn.InputMeta(
            hidden=True,
            description="Window length used for prominence calculation. If `x` is provided, specify in x-units (internally converted to samples); otherwise in samples.",
        ),
    ] = None,
    rel_height: Annotated[
        float,
        fn.InputMeta(
            description="Fallback height factor. If `height` is None, detection height = `rel_height * max(detection signal)`."
        ),
    ] = 0.05,
    width_at_rel_height: Annotated[
        float,
        fn.InputMeta(
            hidden=True,
            description="Relative height at which peak width is measured. 0.5 corresponds to FWHM. Passed to `find_peaks(rel_height=...)`.",
        ),
    ] = 0.5,
    plateau_size: Annotated[
        Optional[int],
        fn.InputMeta(
            hidden=True,
            description="Minimum length of a flat-top (plateau) at the peak. In x-units if `x` is provided, else in samples. See `scipy.signal.find_peaks`.",
        ),
    ] = None,
) -> Tuple[
    Annotated[List[PeakProperties], fn.OutputMeta(description="Peak properties",name="peaks")],
    Annotated[np.ndarray, fn.OutputMeta(description="Normalized X-axis values",name="norm_x")],
    Annotated[np.ndarray, fn.OutputMeta(description="Normalized Y-axis values",name="norm_y")],
]:
    # Tuple[List[PeakProperties], np.ndarray, np.ndarray]:
    """
    Detect peaks on an optional processed signal and report peak bounds and center.

    Parameters
    - y: Original signal for reporting measurements.
    - x: Optional x/axis values. If provided, density normalization preserves indices.
    - on: Optional signal to use for detection (e.g., smoothed/denoised).
    - index_source: How to choose peak center inside detected bounds:
        * "original": argmax on original `_y` within [i,f] (default).
        * "on": keep detection index as-is.
        * "centroid": center-of-mass on `_y` within [i,f].
    """
    peak_lst = []

    y = np.array(y, dtype=float)
    _y = y
    if on is not None:
        y = on

    noise_level = int(noise_level) if noise_level is not None else None
    height = float(height) if height is not None else None
    threshold = float(threshold) if threshold is not None else None
    distance = float(distance) if distance is not None else None
    prominence = float(prominence) if prominence is not None else None
    width = float(width) if width is not None else None
    wlen = float(wlen) if wlen is not None else None
    width_at_rel_height = float(width_at_rel_height)
    plateau_size = float(plateau_size) if plateau_size is not None else None

    height = rel_height * np.max(y) if height is None else height
    noise_level = 5000 if noise_level is None else noise_level

    if x is not None:
        ox = x = np.array(x, dtype=float)
        x, y = density_normalization(
            x,
            y,
        )
        if on is not None:
            _, _y = density_normalization(
                ox,
                _y,
            )
        else:
            _y = y

        xdiff = x[1] - x[0]
        # if x is given width is based on the x scale and has to be converted to index
        if width is not None:
            width = width / xdiff

        # same for distance
        if distance is not None:
            distance = distance / xdiff

        # same for wlen
        if wlen is not None:
            wlen = wlen / xdiff

        # same for plateau_size
        if plateau_size is not None:
            plateau_size = plateau_size / xdiff
    else:
        x = np.arange(len(y))
    # Find the peaks in the copy of the input array
    peaks, _ = find_peaks(
        y,
        threshold=threshold,
        prominence=prominence,
        height=height,
        distance=distance,
        width=max(1, width) if width is not None else None,
        wlen=int(wlen) if wlen is not None else None,
        rel_height=width_at_rel_height,
        plateau_size=plateau_size,
    )

    # Calculate the standard deviation of peak prominences
    rnd = np.random.RandomState(42)
    # Fit a normal distribution to the input array
    noise = estimate_noise(x=x, y=_y) / noise_level
    if peaks is not None:
        try:
            # Add noise to the input array
            y = y + rnd.normal(0, noise, np.shape(y))

            # Find the minimums in the copy of the input array
            mins, _ = find_peaks(-1 * y)

            # Iterate over the peaks
            for peak in peaks:
                # Calculate the prominences of the peak
                # Find the right minimum of the peak
                right_min = mins[np.argmax(mins > peak)]
                if right_min < peak:
                    right_min = len(y) - 1

                try:
                    # Find the left minimum of the peak
                    left_min = np.array(mins)[np.where(np.array(mins) < peak)][-1]
                except IndexError:
                    left_min = 0

                if height is None:
                    # If no height is specified, append the peak bounds to the peak list
                    peak_lst.append([left_min, peak, right_min])

                else:
                    # If a height is specified, append the peak bounds to the peak list
                    # if the peak's value is greater than the height
                    if y[peak] > height:
                        peak_lst.append([left_min, peak, right_min])

        except ValueError:
            # If an error occurs when adding noise to the input array, add stronger noise and try again
            y = y + rnd.normal(0, noise * 100, np.shape(y))
            mins, _ = find_peaks(-1 * y)
            for peak in peaks:
                right_min = mins[np.argmax(mins > peak)]
                if right_min < peak:
                    right_min = len(y) - 1
                try:
                    left_min = np.array(mins)[np.where(np.array(mins) < peak)][-1]
                except IndexError:
                    left_min = 0
                if height is None:
                    # If no height is specified, append the peak bounds to the peak list
                    peak_lst.append([left_min, peak, right_min])
                else:
                    # If a height is specified, append the peak bounds to the peak list
                    # if the peak's value is greater than the height
                    if y[peak] > height:
                        peak_lst.append([left_min, peak, right_min])

    peak_properties_list = []

    for peak_nr, peak in enumerate(peak_lst):
        i_index, index, f_index = peak
        peak_properties = PeakProperties(
            id=str(peak_nr + 1),
            i_index=i_index,
            index=index,
            f_index=f_index,
            xfull=x,
            yfull=_y,
        )
        peak_properties_list.append(peak_properties)

    return peak_properties_list, x, y


@NodeDecorator(
    "span.basics.interpolation_1d",
    name="Interpolation 1D",
    outputs=[
        {
            "name": "x_interpolated",
        },
        {"name": "y_interpolated"},
    ],
)
def interpolation_1d(
    x: np.array, y: np.array, multipled_by: int = 10
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Interpolate the given 1D data to increase the resolution.

    Parameters:
    - x (np.array): The x-values of the data.
    - y (np.array): The y-values of the data.
    - multipled_by (int): The factor by which to multiply the number of points.

    Returns:
    - np.array: The interpolated x-values.
    - np.array: The interpolated y-values.
    """

    f_interpol = interpolate.interp1d(x, y)
    x_interpolated = np.linspace(x[0], x[-1], num=len(x) * multipled_by, endpoint=True)
    y_interpolated = f_interpol(x_interpolated)
    return x_interpolated, y_interpolated


@NodeDecorator(
    "span.basics.force_fit",
    name="Advanced peak finder",
)
def force_peak_finder(
    x: np.array,
    y: np.array,
    basic_peak: PeakProperties,
) -> List[PeakProperties]:
    """
    Breaks down a given main peak into two individual peaks.

    The function works by calculating the first and second derivatives of the signal and
    finding the local maxima and minima of the derivatives. It then determines which peak
    is on the left and right side of the main peak by comparing the distance between the
    main peak and the closest peak on either side.

    Parameters:
    - x (np.array): The x-values of the signal.
    - y (np.array): The y-values of the signal.
    - basic_peak (PeakProperties): The main peak.

    Returns:
    - List[PeakProperties]: A list of two PeakProperties objects, one for each of the
      individual peaks.
    """
    if not isinstance(basic_peak, PeakProperties):
        raise TypeError("The basic peak must be a single PeakProperties object.")

    peak = copy.deepcopy(basic_peak)
    main_peak_i_index = peak.i_index
    main_peak_r_index = peak.index
    main_peak_f_index = peak.f_index
    y_array = y
    x_array = x
    # Calculate first and second derivatives
    y_array_p = np.gradient(y_array, x, axis=-1)
    y_array_pp = np.gradient(y_array_p, x, axis=-1)
    # Smooth derivatives using Gaussian filter
    y_array_p = gaussian_filter1d(y_array_p, 5)
    y_array_pp = gaussian_filter1d(y_array_pp, 5)

    # maxx = [main_peak_r_index]
    # minn = [main_peak_i_index, main_peak_f_index]
    # Find local maxima and minima of derivatives
    max_p = signal.argrelmax(y_array_p)[0]
    min_p = signal.argrelmin(y_array_p)[0]
    max_pp = signal.argrelmax(y_array_pp)[0]
    # min_pp = signal.argrelmin(y_array_pp)[0]

    # main_peak_i_index = peak.i_index
    # main_peak_r_index = peak.index
    # main_peak_f_index = peak.f_index

    # Determine which peak is on the left and right side of the main peak
    if (
        x_array[main_peak_r_index] - x_array[main_peak_i_index]
        > x_array[main_peak_f_index] - x_array[main_peak_r_index]
    ):  # seond peak is in the leftside of the max peak #TODO: fix this
        common_point = max([num for num in max_pp if num < main_peak_r_index])

        # print("Left convoluted")
        peak1 = {
            "I.Index": main_peak_i_index,
            "R.Index": max(
                [num for num in min_p if num < main_peak_r_index]
            ),  # TODO: fix this
            "F.Index": common_point,
        }
        peak2 = {
            "I.Index": common_point,
            "R.Index": main_peak_r_index,
            "F.Index": main_peak_f_index,
        }
    else:
        common_point = next((x for x in max_pp if x > main_peak_r_index), None)
        # print("Right convoluted")
        peak1 = {
            "I.Index": main_peak_i_index,
            "R.Index": main_peak_r_index,
            "F.Index": common_point,
        }
        peak2 = {
            "I.Index": common_point,
            "R.Index": next((x for x in max_p if x > main_peak_r_index), None),
            "F.Index": main_peak_f_index,
        }
    peak_lst = []
    peak_lst.append([peak1["I.Index"], peak1["R.Index"], peak1["F.Index"]])
    peak_lst.append([peak2["I.Index"], peak2["R.Index"], peak2["F.Index"]])

    peak_properties_list = []
    for peak_nr, peak in enumerate(peak_lst):
        peak_properties = PeakProperties(
            id=basic_peak.id + f"_{peak_nr + 1}",
            i_index=peak[0],
            index=peak[1],
            f_index=peak[2],
            xfull=x,
            yfull=y,
        )

        peak_properties_list.append(peak_properties)

    return peak_properties_list


@NodeDecorator(
    id="span.basics.peaks.plot",
    name="Plot peaks",
    default_render_options={"data": {"src": "figure"}},
    outputs=[{"name": "figure"}],
)
def plot_peaks(
    x: np.array,
    y: np.array,
    peaks: List[PeakProperties],
    fill_rectangles: bool = True,
    xaxis_title: str = "x",
    yaxis_title: str = "y",
    title: str = "",
    show_legend: bool = True,
) -> go.Figure:
    fig = go.Figure()

    # Set up line plot
    plot_trace = {"x": x, "y": y, "mode": "lines", "name": "data"}

    fig.add_trace(go.Scatter(**plot_trace))

    # Define a list of colors for the peaks
    peaks_colors = ["orange", "green", "red", "blue"]

    # Add rectangle shapes for each peak
    for index, peak in enumerate(peaks):
        peak_height = peak.y_at_index
        plot_y_min = min(peak.y_at_i_index, peak.y_at_f_index)

        # Create a scatter trace that simulates a rectangle
        fig.add_trace(
            go.Scatter(
                x=[
                    peak.x_at_i_index,
                    peak.x_at_f_index,
                    peak.x_at_f_index,
                    peak.x_at_i_index,
                    peak.x_at_i_index,
                ],
                y=[plot_y_min, plot_y_min, peak_height, peak_height, plot_y_min],
                fill="toself" if fill_rectangles else None,
                fillcolor=peaks_colors[index % len(peaks_colors)]
                if fill_rectangles
                else None,
                opacity=0.3 if fill_rectangles else 1,
                line=dict(width=0 if fill_rectangles else 2),
                mode="lines",
                name=f"Peak {peak.id}",
                legendgroup=f"Peak {peak.id}",  # Group by Peak id
                showlegend=show_legend,
            )
        )
        # Add an X marker at the exact peak position
        fig.add_trace(
            go.Scatter(
                x=[peak.x_at_index],
                y=[peak.y_at_index],
                mode="markers",
                marker=dict(symbol="x", size=10, color="black"),
                legendgroup=f"Peak {peak.id}",  # Same group as rectangle
                showlegend=False,
            )
        )

        if hasattr(peak, "model") and peak.model is not None:
            model = peak.model
            y_fit = model.eval(x=peak.xrange, params=model.make_params())
            fig.add_trace(
                go.Scatter(
                    x=peak.xrange,
                    y=y_fit,
                    mode="lines",
                    name=f"Peak {peak.id} fit",
                    line=dict(
                        dash="dash", color=peaks_colors[index % len(peaks_colors)]
                    ),
                    legendgroup=f"Peak {peak.id}",
                    showlegend=show_legend,
                ),
            )

    # Customize layout (axes labels and title can be added here if needed)
    fig.update_layout(
        xaxis_title=xaxis_title,
        yaxis_title=yaxis_title,
        title=title,
        plot_bgcolor="white",
        paper_bgcolor="white",
        showlegend=show_legend,
        font=dict(family="Arial", size=14),
        xaxis=dict(title_font=dict(size=16), tickfont=dict(size=14)),
        # yaxis=dict(title_font=dict(size=16), tickfont=dict(size=14), tickformat=".2e"),
    )

    return fig


color_map = {
    "C0": "blue",
    "C1": "orange",
    "C2": "green",
    "C3": "red",
    "C4": "purple",
    "C5": "brown",
    "C6": "pink",
    "C7": "gray",
    "C8": "olive",
    "C9": "cyan",
}


@NodeDecorator(
    id="span.basics.fit.plot",
    name="Plot fit 1D",
    default_render_options={"data": {"src": "figure"}},
    outputs=[{"name": "figure"}],
)
def plot_fitted_peaks(peaks: List[PeakProperties]) -> go.Figure:
    peak = peaks[0]
    if not peak.model:
        raise ValueError("No fitting information is available.")

    x_diff = min([np.diff(peak.xfull).mean()])
    minx = min([peak.xfull.min()])
    max_x = max([peak.xfull.max()])
    x_range = np.arange(minx, max_x + x_diff, x_diff)
    y_raw = np.array(
        [
            np.interp(x_range, peak.xfull, peak.yfull, left=np.nan, right=np.nan)
            for peak in peaks
        ]
    )
    y_raw = np.nanmean(y_raw, axis=0)
    # interrpolate nan values
    is_nan = np.isnan(y_raw)
    y_raw[is_nan] = np.interp(x_range[is_nan], x_range[~is_nan], y_raw[~is_nan])

    # Create a subplot with 1 row, 1 column, and a secondary y-axis
    fig = go.Figure()

    # Add the original data trace
    fig.add_trace(
        go.Scatter(
            x=x_range,
            y=y_raw,
            mode="lines",
            name="original",
        ),
    )

    total_y = np.zeros_like(x_range)

    for peak in peaks:
        # add the peak trace
        fig.add_trace(
            go.Scatter(
                x=peak.xrange,
                y=peak.yrange,
                mode="lines",
                name=peak.id,
                legendgroup=peak.id,
                legendgrouptitle={"text": f"Peak {peak.id}"},
            ),
        )

        model = peak.model

        ypeak = model.eval(x=x_range, params=model.make_params())
        total_y += ypeak

        fig.add_trace(
            go.Scatter(
                x=x_range,
                y=ypeak,
                mode="lines",
                name=peak.id + " fit",
                line=dict(dash="dash"),
                legendgroup=peak.id,
            ),
        )

    fig.add_trace(
        go.Scatter(
            x=x_range,
            y=total_y,
            mode="lines",
            name="total fit",
            line=dict(dash="dash"),
        ),
    )

    # callculate r2 between the total fit and the original data
    r2 = 1 - np.sum((y_raw - total_y) ** 2) / np.sum((y_raw - np.mean(y_raw)) ** 2)

    # Update axes labels and legend
    fig.update_layout(
        title={
            "text": f"Fitted peaks score = {np.round(r2, 4)}",
            "x": 0.5,  # Center the title
            "xanchor": "center",
        },
    )

    return fig


@NodeDecorator(
    "span.basics.plot_peak",
    name="Plot Peak",
    outputs=[{"name": "figure"}],
    default_render_options={"data": {"src": "figure"}},
)
def plot_peak(
    peak: PeakProperties,
    x: Optional[np.ndarray] = None,
    y: Optional[np.ndarray] = None,
) -> go.Figure:
    if x is None:
        x = peak.xrange
    else:
        x = x[peak.i_index : peak.f_index]
    if y is None:
        y = peak.yrange
    else:
        y = y[peak.i_index : peak.f_index]

    if x is None or y is None:
        raise ValueError("x and y must be provided or peak must have xfull and yfull")

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=y, mode="lines", name="Signal"))
    fig.add_trace(
        go.Scatter(
            x=[x[peak.index - peak.i_index]],
            y=[y[peak.index - peak.i_index]],
            mode="markers",
            marker=dict(size=10, color="red"),
            name="Peak",
        )
    )
    fig.update_layout(title=f"Peak {peak.id}")
    return fig


fit_peak_node = fn.NodeDecorator(
    id="span.peaks.fit_peak",
    name="Fit Peak",
    outputs=[{"name": "fitted_peak"}, {"name": "model"}, {"name": "fit_result"}],
    separate_process=True,
)(fit_local_peak)


@fn.NodeDecorator(
    id="span.peaks.fit_peaks",
    name="Fit Peaks",
    outputs=[{"name": "fitted_peaks"}, {"name": "model"}, {"name": "fit_results"}],
    separate_thread=True,
)
@fn.controlled_wrapper(fit_peaks, wrapper_attribute="__fnwrapped__")
def fit_peaks_node(
    peaks: List[PeakProperties],
    x: np.ndarray,
    y: np.ndarray,
    model_class: AutoModelEnum = AutoModelEnum.GaussianModel,
    filter_negatives: bool = True,
    baseline_factor: float = 0.001,
    incomplete_threshold: float = 0.8,
    incomplete_x_extend: float = 2.0,
    incomplete_peak_model_class: AutoModelEnum = AutoModelEnum.GaussianModel,
    node: fn.Node = None,
) -> Tuple[List[PeakProperties], Model, ModelResult]:
    _tqdm_kwargs = {
        "desc": "Fitting peaks",
    }
    if node is not None:
        progress = node.progress(**_tqdm_kwargs)
    else:
        progress = tqdm(**_tqdm_kwargs)

    def _cb(params, iter, resid, *args, **kws):
        progress.update(1)

    try:
        result = fit_peaks(
            peaks,
            x,
            y,
            model_class=model_class,
            filter_negatives=filter_negatives,
            baseline_factor=baseline_factor,
            incomplete_threshold=incomplete_threshold,
            incomplete_x_extend=incomplete_x_extend,
            incomplete_peak_model_class=incomplete_peak_model_class,
            iter_cb=_cb,
        )
        return result
    finally:
        progress.close()


peaks_from_fitted_node = fn.NodeDecorator(
    id="span.peaks.peaks_from_fitted",
    name="Peaks from fitted",
    description="converts the fit data in peaks to regular peaks",
    outputs=[{"name": "peaks"}],
)(peaks_from_fitted)

PEAKS_NODE_SHELF = Shelf(
    nodes=[
        peak_finder,
        interpolation_1d,
        force_peak_finder,
        plot_peaks,
        fit_peaks_node,
        fit_peak_node,
        peaks_from_fitted_node,
        plot_fitted_peaks,
        plot_peak,
    ],
    subshelves=[],
    name="Peak analysis",
    description="Tools for the peak analysis of the spectra",
)
