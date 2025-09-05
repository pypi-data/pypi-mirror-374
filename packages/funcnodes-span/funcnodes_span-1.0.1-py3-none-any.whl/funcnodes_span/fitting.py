from typing import List, Type, Tuple
import numpy as np
from lmfit import Model
from lmfit.model import ModelResult
from lmfit.models import GaussianModel
from .peaks import PeakProperties
from funcnodes_lmfit.model import AUTOMODELMAP
import funcnodes as fn

AutoModelEnum = fn.DataEnum("AutoModelEnum", AUTOMODELMAP)
# class AutoModelEnum(fn.DataEnum):
#     GaussianModel = AUTOMODELMAP["GaussianModel"]
#     LorentzianModel = AUTOMODELMAP["LorentzianModel"]


def group_signals(
    x: np.ndarray,
    y: np.ndarray,
    peaks: List[PeakProperties],
    baseline_factor: float = 0.001,
) -> List[List[PeakProperties]]:
    """
    Groups peaks based on the baseline factor and the signal array.

    Args:
        x (np.ndarray): Array of x-values (independent variable).
        y (np.ndarray): Array of y-values (dependent variable).
        peaks (List[PeakProperties]): List of detected peaks.
        baseline_factor (float): Factor to determine the baseline cutoff.

    Returns:
        List[List[PeakProperties]]: List of grouped peaks.
    """

    # Detecting baseline by checking y values that are above a fraction (baseline_factor) of the maximum value
    is_baseline = (np.abs(y) >= np.abs(baseline_factor * y.max())).astype(int)
    baseline_cut = np.unique(
        [0] + np.where(np.diff(is_baseline) != 0)[0].tolist() + [len(is_baseline) - 1]
    )

    # Initialize empty lists for peak groups
    peak_groups: List[List[int]] = [[] for _ in baseline_cut]

    # Assign each peak to its respective group based on start and end indices
    for pi, p in enumerate(peaks):
        ingroup = (baseline_cut >= p.i_index) & (baseline_cut <= p.f_index)

        if ingroup.sum() == 0:
            ingroup[(baseline_cut >= p.i_index).argmax()] = True

        for i in range(len(ingroup)):
            if ingroup[i]:
                peak_groups[i].append(pi)

    connected_peaks = []
    current_peak_group = set()

    # Group connected peaks
    for pg in peak_groups:
        if len(pg) == 0:
            if len(current_peak_group) > 0:
                connected_peaks.append(list(current_peak_group))
            current_peak_group = set()
        else:
            current_peak_group.update(pg)

    if len(current_peak_group) > 0:
        connected_peaks.append(list(current_peak_group))

    # Return a list of grouped PeakProperties
    return [[peaks[pi] for pi in cp] for cp in connected_peaks if len(cp) > 0]


def get_submodel_by_prefix(model: Model, prefix: str) -> Model:
    """
    Get a submodel from a composite model by prefix.

    Args:
        model (Model): The composite model.
        prefix (str): The prefix of the submodel to retrieve.

    Returns:
        Model: The submodel with the specified prefix.
    """
    for m in model.components:
        if m.prefix == prefix:
            return m
    raise ValueError(f"No submodel found with prefix {prefix}.")


def fit_local_peak(
    x: np.ndarray,
    y: np.ndarray,
    peak: PeakProperties,
    model_class: Type[Model] = GaussianModel,
    filter_negatives: bool = True,
    incomplete_peak_model_class: Type[Model] = GaussianModel,
    incomplete_threshold: float = 0.8,
    incomplete_x_extend: float = 2.0,
    iter_cb=None,
) -> Tuple[PeakProperties, Model, ModelResult]:
    """
    Fits a local peak with the provided model class.

    Args:
        x (np.ndarray): Array of x-values.
        y (np.ndarray): Array of y-values.
        peak (PeakProperties): Peak properties for the specific peak.
        model_class: Model class for fitting, defaults to GaussianModel.
        filter_negatives (bool): Whether to filter negative y-values.
        incomplete_peak_model_class: Model class for incomplete peaks.
        incomplete_threshold (float): Threshold to consider a peak as incomplete.
        incomplete_x_extend (float): Factor to extend the x-range for incomplete peaks.

    Returns:
        Model: The fitted model for the peak.
    """
    x = np.asarray(x)
    y = np.asarray(y)

    model_class = AutoModelEnum.v(model_class)
    incomplete_peak_model_class = AutoModelEnum.v(incomplete_peak_model_class)

    pf = f"p{peak.id}_"
    model = model_class(prefix=pf)  # Initialize the model
    left = peak.i_index  # Left index of peak
    right = peak.f_index + 1  # Right index of peak

    yf = y[left:right]
    xf = x[left:right]

    # If the peak appears incomplete, extend the peak region
    local_min = yf.min()
    local_max = yf.max()

    if peak.xfull is None:
        peak.xfull = x
    if peak.yfull is None:
        peak.yfull = y

    if np.abs(yf[-1] - yf[0]) > incomplete_threshold * (local_max - local_min):
        # Handle incomplete peak by extending the range and filling gaps
        m_complete = incomplete_peak_model_class()
        guess = m_complete.guess(data=yf, x=xf)
        guess["center"].set(min=min(xf), max=max(xf))
        fr_complete = m_complete.fit(data=yf, x=xf, params=guess, iter_cb=iter_cb)

        fwhm = 2 * np.sqrt(2 * np.log(2)) * fr_complete.params["sigma"].value
        center = fr_complete.params["center"].value
        xmeandiff = np.diff(xf).mean()

        # Extend x range for incomplete peaks
        xnew = np.arange(
            min(xf.min(), center - incomplete_x_extend * fwhm),
            max(xf.max(), center + incomplete_x_extend * fwhm),
            xmeandiff,
        )

        # Interpolate the y-values over the new extended x range
        yf = np.interp(xnew, xf, yf, left=np.nan, right=np.nan)
        xf = xnew

        # Fill NaNs with the fitted gaussian
        nan_filter = np.isnan(yf)
        yf[nan_filter] = fr_complete.eval(x=xf[nan_filter], params=fr_complete.params)

    if filter_negatives:
        # Filter out negative y-values to avoid erroneous fitting
        negativ_filter = yf >= 0
        yf = yf[negativ_filter]
        xf = xf[negativ_filter]

    # Perform the fitting using the model and guessed parameters
    guess = model.guess(data=yf, x=xf)
    fr = model.fit(data=yf, x=xf, params=guess)

    # Update the model with the fitted parameters
    for pname, param in fr.params.items():
        v = param.value
        data = {"value": v}
        if "center" in pname:
            data["min"] = min(xf.min(), v)
            data["max"] = max(xf.max(), v)

        if "amplitude" in pname:
            if v > 0:
                data["min"] = v / 10
                data["max"] = 2 * v
            if v < 0:
                data["max"] = v / 10
                data["min"] = 2 * v

        # if "sigma" in pname:
        #     data["min"] = v / 1.1
        #     data["max"] = 1.1 * v

        if v != 0:
            model.set_param_hint(pname, **data)

    peak.model = model

    return peak, model, fr


def fit_peak_group(
    x,
    y,
    peaks: List[PeakProperties],
    model_class: Type[Model] = GaussianModel,
    filter_negatives: bool = True,
    incomplete_threshold: float = 0.8,
    incomplete_x_extend: float = 2.0,
    incomplete_peak_model_class: Type[Model] = GaussianModel,
    iter_cb=None,
) -> Model:
    """
    Fits a group of peaks using a model class.

    Args:
        x (np.ndarray): Array of x-values.
        y (np.ndarray): Array of y-values.
        peaks (List[PeakProperties]): List of peaks to fit.
        model_class: Model class for fitting, defaults to GaussianModel.
        filter_negatives (bool): Whether to filter negative y-values.
        incomplete_threshold (float): Threshold to consider a peak as incomplete.
        incomplete_x_extend (float): Factor to extend the x-range for incomplete peaks.
        incomplete_peak_model_class: Model class for incomplete peaks.

    Returns:
        Model: The fitted model for the group of peaks.
    """

    x = np.asarray(x)
    y = np.asarray(y)

    model_class = AutoModelEnum.v(model_class)
    incomplete_peak_model_class = AutoModelEnum.v(incomplete_peak_model_class)

    groupmodel = None
    most_left = min([p.i_index for p in peaks])  # Find the leftmost index in the group
    most_right = max(
        [p.f_index for p in peaks]
    )  # Find the rightmost index in the group

    # Fit each peak in the group
    for peak in peaks:
        _, peakmodel, _ = fit_local_peak(
            x=x,
            y=y,
            peak=peak,
            model_class=model_class,
            filter_negatives=filter_negatives,
            incomplete_threshold=incomplete_threshold,
            incomplete_x_extend=incomplete_x_extend,
            incomplete_peak_model_class=incomplete_peak_model_class,
            iter_cb=iter_cb,
        )
        # If no group model exists, initialize it with the first peak model
        if groupmodel is None:
            groupmodel = peakmodel
        else:
            # Combine the models for the group of peaks
            groupmodel += peakmodel

    # Fit the model to the combined data of the peak group
    xgroup = x[most_left : most_right + 1]
    ygroup = y[most_left : most_right + 1]
    groupfit = groupmodel.fit(data=ygroup, x=xgroup, iter_cb=iter_cb)

    # Update the group model with the best-fit parameters
    for pname, param in groupfit.params.items():
        v = param.value
        groupmodel.set_param_hint(pname, value=v)

    for peak in peaks:
        peak.model = get_submodel_by_prefix(groupmodel, f"p{peak.id}_")

    return groupmodel


def fit_peaks(
    peaks: List[PeakProperties],
    x: np.ndarray,
    y: np.ndarray,
    model_class: AutoModelEnum = AutoModelEnum.GaussianModel,
    filter_negatives: bool = True,
    baseline_factor: float = 0.001,
    incomplete_threshold: float = 0.8,
    incomplete_x_extend: float = 2.0,
    incomplete_peak_model_class: AutoModelEnum = AutoModelEnum.GaussianModel,
    iter_cb=None,
) -> Tuple[List[PeakProperties], Model, ModelResult]:
    """
    Fits multiple peaks in a 1D signal by grouping the peaks based on a baseline cutoff,
    fitting each group of peaks with a provided model, and then fitting the entire signal
    globally using the combined peak models.

    The function follows a multi-step process:

    1. **Group Peaks by Baseline**:
        Peaks are grouped together based on a baseline factor that determines where
        the signal significantly deviates from a baseline. The baseline cutoff is defined
        as a fraction of the maximum y-value. Peaks within the same baseline region
        are grouped together for simultaneous fitting.

    2. **Fit Individual Peak Groups**:
        Each group of peaks is fitted independently. The fitting process begins by
        fitting individual peaks within each group using the `fit_local_peak` function.
        If a peak is identified as incomplete (e.g., if its start or end is truncated),
        the x-range of the signal is extended, and a secondary model (typically a
        Gaussian) is used to extend and complete the peak.

        For each group, the individual peak models are summed together to create
        a combined model for the entire group. This model is then fitted to the signal
        data for that peak group.

    3. **Global Signal Fitting**:
        Once all peak groups have been fitted independently, their combined models
        are summed together to create a global model that represents the entire signal.
        This global model is then fitted to the entire signal (the full x and y arrays).
        The parameters of the global model are updated with the best-fit values obtained
        from the fitting process.

    4. **Return the Global Model**:
        The global model, which now represents the best fit for the entire signal based
        on the detected peaks, is returned. This model contains the best-fit parameters
        for each peak and group of peaks in the signal, allowing for further analysis or
        visualization.

    Args:
        x (np.ndarray): Array of x-values.
        y (np.ndarray): Array of y-values.
        peaks (List[PeakProperties]): List of detected peaks.
        model_class: Model class for fitting, defaults to GaussianModel.
        filter_negatives (bool): Whether to filter negative y-values.
        baseline_factor (float): Factor to determine the baseline cutoff.
        incomplete_threshold (float): Threshold to consider a peak as incomplete.
        incomplete_x_extend (float): Factor to extend the x-range for incomplete peaks.
        incomplete_peak_model_class: Model class for incomplete peaks.

    Returns:
        Model: The fitted model for the global signal.
    """
    model_class = AutoModelEnum.v(model_class)
    incomplete_peak_model_class = AutoModelEnum.v(incomplete_peak_model_class)
    x = np.asarray(x)
    y = np.asarray(y)

    if len(peaks) == 0:
        raise ValueError("No peaks provided for fitting.")

    # Group peaks based on the baseline factor
    connected_peaks = group_signals(x, y, peaks, baseline_factor=baseline_factor)
    if len(connected_peaks) == 0:
        raise ValueError("No peaks after grouping.")

    global_model = None
    # Fit each peak group
    for pg in connected_peaks:
        if len(pg) == 0:
            continue
        m = fit_peak_group(
            x,
            y,
            pg,
            model_class=model_class,
            filter_negatives=filter_negatives,
            incomplete_threshold=incomplete_threshold,
            incomplete_x_extend=incomplete_x_extend,
            incomplete_peak_model_class=incomplete_peak_model_class,
            iter_cb=iter_cb,
        )
        if global_model is None:
            global_model = m
        else:
            # Combine models for all peak groups
            global_model += m

    if global_model is None:
        raise ValueError("No model created")

    # Fit the global model to the full data
    global_fit = global_model.fit(data=y, x=x, iter_cb=iter_cb)

    # Update the global model with the best-fit parameters
    for pname, param in global_fit.params.items():
        v = param.value
        global_model.set_param_hint(pname, value=v)

    for peak in peaks:
        peak.model = get_submodel_by_prefix(global_model, f"p{peak.id}_")

    return peaks, global_model, global_fit


def peaks_from_fitted(fitted_peaks: List[PeakProperties]) -> List[PeakProperties]:
    peaks = []
    from .peak_analysis import peak_finder  # noaq Avoid circular import

    for p in fitted_peaks:
        model = p.model
        mparams = model.make_params()
        y = model.eval(x=p.xfull, params=mparams)
        pf: List[PeakProperties] = peak_finder.o_func(y=y, x=p.xfull)[0]
        if len(pf) != 1:
            raise ValueError("Expected one peak")
        pf = pf[0]
        pf._id = f"fitted_{p.id}"
        pf.model = model
        p.add_serializable_property("model", str(model))
        for k, v in mparams.items():
            p.add_serializable_property(k.replace(model.prefix, ""), v.value)
        peaks.append(pf)

    return peaks
