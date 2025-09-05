import funcnodes as fn
from funcnodes import NodeDecorator, Shelf
import numpy as np
from typing import Optional, Tuple, Union, List
import pybaselines
from scipy import sparse
from scipy.sparse.linalg import spsolve
from scipy.signal import savgol_filter
from .normalization import density_normalization
from ._baseline import estimate_baseline_regions


def baselinewrapper(func):
    @fn.signaturewrapper(func)
    def blw(
        data: np.ndarray,
        *args,
        x_data: Optional[np.ndarray] = None,
        regions: Optional[np.ndarray] = None,
        estimate_window: Optional[float] = None,
        **kwargs,
    ) -> Tuple[np.ndarray, np.ndarray, dict]:
        if regions is None and estimate_window is not None:
            pre_bl, _ = func(data, *args, x_data=x_data, **kwargs)
            pre_flatted = data - pre_bl
            y_bl, regions = estimate_baseline_regions(
                x_data, data, pre_flatted, estimate_window
            )

        if not np.any(regions):
            regions = None

        if regions is not None:
            _data = data[regions]
            if x_data is not None:
                _x_data = x_data[regions]
            else:
                _x_data = x_data
        else:
            _data = data
            _x_data = x_data

        baseline, params = func(_data, *args, x_data=_x_data, **kwargs)

        if regions is not None:
            if x_data is None:
                x_data = np.linspace(-1, 1, len(data))
            baseline = np.interp(x_data, x_data[regions], baseline)

        baseline_corrected = data - baseline

        return baseline_corrected, baseline, params

    return blw


class CostFunction(fn.DataEnum):
    asymmetric_indec = "asymmetric_indec"
    asymmetric_truncated_quadratic = "asymmetric_truncated_quadratic"
    asymmetric_huber = "asymmetric_huber"


@NodeDecorator(
    "pybaselines.polynomial.goldindec",
    name="goldindec",
    outputs=[
        {"name": "baseline_corrected"},
        {"name": "baseline"},
        {"name": "params"},
    ],
)
@fn.controlled_wrapper(
    pybaselines.polynomial.goldindec, wrapper_attribute="__fnwrapped__"
)
@baselinewrapper
def _goldindec(
    data: np.ndarray,
    x_data: Optional[np.ndarray] = None,
    regions: Optional[np.ndarray] = None,
    estimate_window: Optional[float] = None,
    poly_order: int = 2,
    tol: float = 0.001,
    max_iter: int = 250,
    weights: Optional[np.ndarray] = None,
    cost_function: CostFunction = CostFunction.asymmetric_indec,
    peak_ratio: float = 0.5,
    alpha_factor: float = 0.99,
    tol_2: float = 0.001,
    tol_3: float = 1e-06,
    max_iter_2: int = 100,
    return_coef: bool = False,
) -> Tuple[np.ndarray, np.ndarray, dict]:
    cost_function = CostFunction.v(cost_function)
    baseline, params = pybaselines.polynomial.goldindec(
        data,
        x_data=x_data,
        poly_order=poly_order,
        tol=tol,
        max_iter=max_iter,
        weights=weights,
        cost_function=cost_function,
        peak_ratio=peak_ratio,
        alpha_factor=alpha_factor,
        tol_2=tol_2,
        tol_3=tol_3,
        return_coef=return_coef,
        max_iter_2=max_iter_2,
    )
    return baseline, params


@NodeDecorator(
    "pybaselines.polynomial.imodpoly",
    name="imodpoly",
    outputs=[
        {"name": "baseline_corrected"},
        {"name": "baseline"},
        {"name": "params"},
    ],
)
@fn.controlled_wrapper(
    pybaselines.polynomial.imodpoly, wrapper_attribute="__fnwrapped__"
)
@baselinewrapper
def _imodpoly(
    data: np.ndarray,
    x_data: Optional[np.ndarray] = None,
    regions: Optional[np.ndarray] = None,
    estimate_window: Optional[float] = None,
    poly_order: int = 2,
    max_iter: int = 250,
    tol: float = 1e-3,
    weights: Optional[np.ndarray] = None,
    num_std: float = 1.0,
    use_original: bool = False,
    mask_initial_peaks: bool = False,
    return_coef: bool = False,
) -> Tuple[np.ndarray, np.ndarray, dict]:
    baseline, params = pybaselines.polynomial.imodpoly(
        data,
        x_data=x_data,
        poly_order=poly_order,
        max_iter=max_iter,
        tol=tol,
        weights=weights,
        num_std=num_std,
        use_original=use_original,
        return_coef=return_coef,
        mask_initial_peaks=mask_initial_peaks,
    )
    return baseline, params


@NodeDecorator(
    "pybaselines.polynomial.loess",
    name="loess",
    outputs=[
        {"name": "baseline_corrected"},
        {"name": "baseline"},
        {"name": "params"},
    ],
)
@fn.controlled_wrapper(pybaselines.polynomial.loess, wrapper_attribute="__fnwrapped__")
@baselinewrapper
def _loess(
    data: np.ndarray,
    x_data: Optional[np.ndarray] = None,
    regions: Optional[np.ndarray] = None,
    estimate_window: Optional[float] = None,
    fraction: float = 0.2,
    total_points: Optional[int] = None,
    scale: float = 3.0,
    poly_order: int = 1,
    max_iter: int = 10,
    tol: float = 1e-3,
    symmetric_weights: bool = False,
    use_threshold: bool = False,
    weights: Optional[np.ndarray] = None,
    num_std: float = 1.0,
    use_original: bool = False,
    conserve_memory: bool = False,
    delta: float = 0.0,
    return_coef: bool = False,
) -> Tuple[np.ndarray, np.ndarray, dict]:
    baseline, params = pybaselines.polynomial.loess(
        data,
        x_data=x_data,
        fraction=fraction,
        total_points=total_points,
        scale=scale,
        poly_order=poly_order,
        max_iter=max_iter,
        tol=tol,
        weights=weights,
        num_std=num_std,
        use_original=use_original,
        symmetric_weights=symmetric_weights,
        use_threshold=use_threshold,
        conserve_memory=conserve_memory,
        return_coef=return_coef,
        delta=delta,
    )
    return baseline, params


@NodeDecorator(
    "pybaselines.polynomial.modpoly",
    name="modpoly",
    outputs=[
        {"name": "baseline_corrected"},
        {"name": "baseline"},
        {"name": "params"},
    ],
)
@fn.controlled_wrapper(
    pybaselines.polynomial.modpoly, wrapper_attribute="__fnwrapped__"
)
@baselinewrapper
def _modpoly(
    data: np.ndarray,
    x_data: Optional[np.ndarray] = None,
    regions: Optional[np.ndarray] = None,
    estimate_window: Optional[float] = None,
    poly_order: int = 2,
    max_iter: int = 250,
    tol: float = 1e-3,
    weights: Optional[np.ndarray] = None,
    use_original: bool = False,
    mask_initial_peaks: bool = False,
    return_coef: bool = False,
) -> Tuple[np.ndarray, np.ndarray, dict]:
    baseline, params = pybaselines.polynomial.modpoly(
        data,
        x_data=x_data,
        poly_order=poly_order,
        max_iter=max_iter,
        tol=tol,
        weights=weights,
        use_original=use_original,
        mask_initial_peaks=mask_initial_peaks,
        return_coef=return_coef,
    )
    return baseline, params


class PenalizedPolyCostFunction(fn.DataEnum):
    asymmetric_truncated_quadratic = "asymmetric_truncated_quadratic"
    symmetric_truncated_quadratic = "symmetric_truncated_quadratic"
    asymmetric_huber = "asymmetric_huber"
    symmetric_huber = "symmetric_huber"
    asymmetric_indec = "asymmetric_indec"
    symmetric_indec = "symmetric_indec"


@NodeDecorator(
    "pybaselines.polynomial.penalized_poly",
    name="penalized_poly",
    outputs=[
        {"name": "baseline_corrected"},
        {"name": "baseline"},
        {"name": "params"},
    ],
)
@fn.controlled_wrapper(
    pybaselines.polynomial.penalized_poly, wrapper_attribute="__fnwrapped__"
)
@baselinewrapper
def _penalized_poly(
    data: np.ndarray,
    x_data: Optional[np.ndarray] = None,
    regions: Optional[np.ndarray] = None,
    estimate_window: Optional[float] = None,
    poly_order: int = 2,
    max_iter: int = 250,
    tol: float = 1e-3,
    weights: Optional[np.ndarray] = None,
    cost_function: PenalizedPolyCostFunction = PenalizedPolyCostFunction.asymmetric_truncated_quadratic,
    threshold: Optional[float] = None,
    alpha_factor: float = 0.99,
    return_coef: bool = False,
) -> Tuple[np.ndarray, np.ndarray, dict]:
    cost_function = PenalizedPolyCostFunction.v(cost_function)
    baseline, params = pybaselines.polynomial.penalized_poly(
        data,
        x_data=x_data,
        poly_order=poly_order,
        max_iter=max_iter,
        tol=tol,
        weights=weights,
        cost_function=cost_function,
        threshold=threshold,
        alpha_factor=alpha_factor,
        return_coef=return_coef,
    )
    return baseline, params


@NodeDecorator(
    "pybaselines.polynomial.poly",
    name="poly",
    outputs=[
        {"name": "baseline_corrected"},
        {"name": "baseline"},
        {"name": "params"},
    ],
)
@fn.controlled_wrapper(pybaselines.polynomial.poly, wrapper_attribute="__fnwrapped__")
@baselinewrapper
def _poly(
    data: np.ndarray,
    x_data: Optional[np.ndarray] = None,
    regions: Optional[np.ndarray] = None,
    estimate_window: Optional[float] = None,
    poly_order: int = 2,
    weights: Optional[np.ndarray] = None,
    return_coef: bool = False,
) -> Tuple[np.ndarray, np.ndarray, dict]:
    baseline, params = pybaselines.polynomial.poly(
        data,
        x_data=x_data,
        poly_order=poly_order,
        weights=weights,
        return_coef=return_coef,
    )
    return baseline, params


@NodeDecorator(
    "pybaselines.polynomial.quant_reg",
    name="quant_reg",
    outputs=[
        {"name": "baseline_corrected"},
        {"name": "baseline"},
        {"name": "params"},
    ],
)
@fn.controlled_wrapper(
    pybaselines.polynomial.quant_reg, wrapper_attribute="__fnwrapped__"
)
@baselinewrapper
def _quant_reg(
    data: np.ndarray,
    x_data: Optional[np.ndarray] = None,
    regions: Optional[np.ndarray] = None,
    estimate_window: Optional[float] = None,
    poly_order: int = 2,
    quantile: float = 0.05,
    max_iter: int = 250,
    tol: float = 1e-6,
    weights: Optional[np.ndarray] = None,
    eps: Optional[float] = None,
    return_coef: bool = False,
) -> Tuple[np.ndarray, np.ndarray, dict]:
    baseline, params = pybaselines.polynomial.quant_reg(
        data,
        x_data=x_data,
        poly_order=poly_order,
        max_iter=max_iter,
        tol=tol,
        weights=weights,
        quantile=quantile,
        eps=eps,
        return_coef=return_coef,
    )
    return baseline, params


POLYNOMIAL_NODE_SHELF = Shelf(
    nodes=[_goldindec, _imodpoly, _loess, _modpoly, _penalized_poly, _poly, _quant_reg],
    subshelves=[],
    name="Polynomial",
    description="Fits a polynomial baseline",
)


@NodeDecorator(
    "pybaselines.whittaker.airpls",
    name="airpls",
    outputs=[
        {"name": "baseline_corrected"},
        {"name": "baseline"},
        {"name": "params"},
    ],
)
@fn.controlled_wrapper(pybaselines.whittaker.airpls, wrapper_attribute="__fnwrapped__")
@baselinewrapper
def _airpls(
    data: np.ndarray,
    x_data: Optional[np.ndarray] = None,
    regions: Optional[np.ndarray] = None,
    estimate_window: Optional[float] = None,
    lam: float = 1000000.0,
    diff_order: int = 2,
    max_iter: int = 50,
    tol: float = 1e-3,
    weights: Optional[np.ndarray] = None,
) -> Tuple[np.ndarray, np.ndarray, dict]:
    baseline, params = pybaselines.whittaker.airpls(
        data,
        x_data=x_data,
        lam=lam,
        max_iter=max_iter,
        tol=tol,
        weights=weights,
        diff_order=diff_order,
    )
    return baseline, params


@NodeDecorator(
    "pybaselines.whittaker.arpls",
    name="arpls",
    outputs=[
        {"name": "baseline_corrected"},
        {"name": "baseline"},
        {"name": "params"},
    ],
)
@fn.controlled_wrapper(pybaselines.whittaker.arpls, wrapper_attribute="__fnwrapped__")
@baselinewrapper
def _arpls(
    data: np.ndarray,
    x_data: Optional[np.ndarray] = None,
    regions: Optional[np.ndarray] = None,
    estimate_window: Optional[float] = None,
    lam: float = 100000.0,
    diff_order: int = 2,
    max_iter: int = 50,
    tol: float = 1e-3,
    weights: Optional[np.ndarray] = None,
) -> Tuple[np.ndarray, np.ndarray, dict]:
    baseline, params = pybaselines.whittaker.arpls(
        data,
        x_data=x_data,
        lam=lam,
        max_iter=max_iter,
        tol=tol,
        weights=weights,
        diff_order=diff_order,
    )
    return baseline, params


@NodeDecorator(
    "pybaselines.whittaker.asls",
    name="asls",
    outputs=[
        {"name": "baseline_corrected"},
        {"name": "baseline"},
        {"name": "params"},
    ],
)
@fn.controlled_wrapper(pybaselines.whittaker.asls, wrapper_attribute="__fnwrapped__")
@baselinewrapper
def _asls(
    data: np.ndarray,
    x_data: Optional[np.ndarray] = None,
    regions: Optional[np.ndarray] = None,
    estimate_window: Optional[float] = None,
    lam: float = 1000000.0,
    p: float = 0.01,
    diff_order: int = 2,
    max_iter: int = 50,
    tol: float = 1e-3,
    weights: Optional[np.ndarray] = None,
) -> Tuple[np.ndarray, np.ndarray, dict]:
    baseline, params = pybaselines.whittaker.asls(
        data,
        x_data=x_data,
        lam=lam,
        p=p,
        max_iter=max_iter,
        tol=tol,
        weights=weights,
        diff_order=diff_order,
    )
    return baseline, params


@NodeDecorator(
    "pybaselines.whittaker.aspls",
    name="aspls",
    outputs=[
        {"name": "baseline_corrected"},
        {"name": "baseline"},
        {"name": "params"},
    ],
)
@fn.controlled_wrapper(pybaselines.whittaker.aspls, wrapper_attribute="__fnwrapped__")
@baselinewrapper
def _aspls(
    data: np.ndarray,
    x_data: Optional[np.ndarray] = None,
    regions: Optional[np.ndarray] = None,
    estimate_window: Optional[float] = None,
    lam: float = 100000.0,
    alpha: Optional[np.ndarray] = None,
    diff_order: int = 2,
    max_iter: int = 100,
    tol: float = 1e-3,
    weights: Optional[np.ndarray] = None,
) -> Tuple[np.ndarray, np.ndarray, dict]:
    baseline, params = pybaselines.whittaker.aspls(
        data,
        x_data=x_data,
        lam=lam,
        alpha=alpha,
        max_iter=max_iter,
        tol=tol,
        weights=weights,
        diff_order=diff_order,
    )
    return baseline, params


@NodeDecorator(
    "pybaselines.whittaker.derpsalsa",
    name="derpsalsa",
    outputs=[
        {"name": "baseline_corrected"},
        {"name": "baseline"},
        {"name": "params"},
    ],
)
@fn.controlled_wrapper(
    pybaselines.whittaker.derpsalsa, wrapper_attribute="__fnwrapped__"
)
@baselinewrapper
def _derpsalsa(
    data: np.ndarray,
    x_data: Optional[np.ndarray] = None,
    regions: Optional[np.ndarray] = None,
    estimate_window: Optional[float] = None,
    lam: float = 1000000.0,
    p: float = 0.01,
    k: Optional[float] = None,
    diff_order: int = 2,
    max_iter: int = 50,
    weights: Optional[np.ndarray] = None,
    smooth_half_window: Optional[int] = None,
    num_smooths: int = 16,
) -> Tuple[np.ndarray, np.ndarray, dict]:
    baseline, params = pybaselines.whittaker.derpsalsa(
        data,
        x_data=x_data,
        lam=lam,
        p=p,
        max_iter=max_iter,
        k=k,
        weights=weights,
        diff_order=diff_order,
        smooth_half_window=smooth_half_window,
        num_smooths=num_smooths,
    )
    return baseline, params


@NodeDecorator(
    "pybaselines.whittaker.drpls",
    name="drpls",
    outputs=[
        {"name": "baseline_corrected"},
        {"name": "baseline"},
        {"name": "params"},
    ],
)
@fn.controlled_wrapper(pybaselines.whittaker.drpls, wrapper_attribute="__fnwrapped__")
@baselinewrapper
def _drpls(
    data: np.ndarray,
    x_data: Optional[np.ndarray] = None,
    regions: Optional[np.ndarray] = None,
    estimate_window: Optional[float] = None,
    lam: float = 100000.0,
    eta: float = 0.5,
    max_iter: int = 50,
    tol: float = 1e-3,
    diff_order: int = 2,
    weights: Optional[np.ndarray] = None,
) -> Tuple[np.ndarray, np.ndarray, dict]:
    baseline, params = pybaselines.whittaker.drpls(
        data,
        x_data=x_data,
        lam=lam,
        eta=eta,
        max_iter=max_iter,
        weights=weights,
        diff_order=diff_order,
        tol=tol,
    )
    return baseline, params


@NodeDecorator(
    "pybaselines.whittaker.iarpls",
    name="iarpls",
    outputs=[
        {"name": "baseline_corrected"},
        {"name": "baseline"},
        {"name": "params"},
    ],
)
@fn.controlled_wrapper(pybaselines.whittaker.iarpls, wrapper_attribute="__fnwrapped__")
@baselinewrapper
def _iarpls(
    data: np.ndarray,
    x_data: Optional[np.ndarray] = None,
    regions: Optional[np.ndarray] = None,
    estimate_window: Optional[float] = None,
    lam: float = 100000.0,
    max_iter: int = 50,
    tol: float = 1e-3,
    diff_order: int = 2,
    weights: Optional[np.ndarray] = None,
) -> Tuple[np.ndarray, np.ndarray, dict]:
    baseline, params = pybaselines.whittaker.iarpls(
        data,
        x_data=x_data,
        lam=lam,
        max_iter=max_iter,
        weights=weights,
        diff_order=diff_order,
        tol=tol,
    )
    return baseline, params


@NodeDecorator(
    "pybaselines.whittaker.iasls",
    name="iasls",
    outputs=[
        {"name": "baseline_corrected"},
        {"name": "baseline"},
        {"name": "params"},
    ],
)
@fn.controlled_wrapper(pybaselines.whittaker.iasls, wrapper_attribute="__fnwrapped__")
@baselinewrapper
def _iasls(
    data: np.ndarray,
    x_data: Optional[np.ndarray] = None,
    regions: Optional[np.ndarray] = None,
    estimate_window: Optional[float] = None,
    lam: float = 100000.0,
    p: float = 0.5,
    lam_1: float = 0.0001,
    max_iter: int = 50,
    tol: float = 1e-3,
    diff_order: int = 2,
    weights: Optional[np.ndarray] = None,
) -> Tuple[np.ndarray, np.ndarray, dict]:
    baseline, params = pybaselines.whittaker.iasls(
        data,
        x_data=x_data,
        lam=lam,
        max_iter=max_iter,
        lam_1=lam_1,
        p=p,
        weights=weights,
        diff_order=diff_order,
        tol=tol,
    )
    return baseline, params


@NodeDecorator(
    "pybaselines.whittaker.psalsa",
    name="psalsa",
    outputs=[
        {"name": "baseline_corrected"},
        {"name": "baseline"},
        {"name": "params"},
    ],
)
@fn.controlled_wrapper(pybaselines.whittaker.psalsa, wrapper_attribute="__fnwrapped__")
@baselinewrapper
def _psalsa(
    data: np.ndarray,
    x_data: Optional[np.ndarray] = None,
    regions: Optional[np.ndarray] = None,
    estimate_window: Optional[float] = None,
    lam: float = 100000.0,
    p: float = 0.5,
    k: Optional[float] = None,
    max_iter: int = 50,
    tol: float = 1e-3,
    diff_order: int = 2,
    weights: Optional[np.ndarray] = None,
) -> Tuple[np.ndarray, np.ndarray, dict]:
    baseline, params = pybaselines.whittaker.psalsa(
        data,
        x_data=x_data,
        lam=lam,
        max_iter=max_iter,
        p=p,
        k=k,
        weights=weights,
        diff_order=diff_order,
        tol=tol,
    )
    return baseline, params


@fn.NodeDecorator(
    "baselines.whittaker.flatfit",
    name="FlatFit",
    outputs=[
        {"name": "baseline_corrected"},
        {"name": "baseline"},
        {"name": "params"},
    ],
)
@baselinewrapper
def flatfit(
    data: np.ndarray,
    x_data: Optional[np.ndarray] = None,
    regions: Optional[np.ndarray] = None,
    estimate_window: Optional[float] = None,
    smoothness: float = 1,
    p: float = 0.03,
) -> Tuple[np.ndarray, np.ndarray, dict]:
    """
    FlatFit: least squares weighted by inverse scale of 1st and 2nd derivatives with smoothness penalty

    Parameters
    ----------

    data: ArrayLike
        1D data

    smoothness: float
        size of smoothness penalty

    p: float
        relative size of Savitzky-Golay filter

    Returns
    -------
    NDArray
        values that minimize the asymmetric squared error with smoothness penalty

    Description
    -----------

    This routine finds vector `z` that minimized:

    `(y-z).T @ W @ (y-z) + smoothness * z.T @ D.T @ D @ z`

    where `W` is determined by slope and curvature at given point

    """

    y = np.array(data)
    if x_data is not None:
        _x_data = np.array(x_data, dtype=float)
        o_x = _x_data
        _x_data, y = density_normalization(
            _x_data,
            y,
        )
    else:
        _x_data = np.linspace(-1, 1, len(y))
        o_x = _x_data

    assert len(y.shape) == 1, "Incorrect data input shape for AsLS"
    assert len(y) > 3, "At least 4 data points muts be provided for AsLS"

    L = len(y)

    # scale lambda to maintain invariance for sampling frequency
    lamb = smoothness * L**4

    # calculate w
    filter_window = max(4, int(L * p))
    slope = savgol_filter(y, filter_window, 3, deriv=1)
    curvature = np.gradient(slope)
    slope = slope**2
    slope /= np.sum(slope)
    curvature = curvature**2
    curvature /= np.sum(curvature)

    w = 1 / (slope + curvature + 1e-10)

    # calculate baseline

    D = sparse.diags([1, -2, 1], [0, -1, -2], shape=(L, L - 2))
    H = lamb * D.dot(D.transpose())

    W = sparse.spdiags(w, 0, L, L)
    Z = W + H
    z = spsolve(Z, w * y)

    z_interpolated = np.interp(o_x, _x_data, z)
    baseline = z_interpolated
    params = {
        "smoothness": smoothness,
        "p": p,
        "lambda": lamb,
        "filter_window": filter_window,
    }
    return baseline, params


WHITTAKER_NODE_SHELF = Shelf(
    nodes=[
        flatfit,
        _airpls,
        _arpls,
        _asls,
        _aspls,
        _derpsalsa,
        _drpls,
        _iarpls,
        _iasls,
        _psalsa,
    ],
    subshelves=[],
    name="Whittaker",
    description="Fits a Whittaker baseline",
)


@NodeDecorator(
    "pybaselines.morphological.amormol",
    name="amormol",
    outputs=[
        {"name": "baseline_corrected"},
        {"name": "baseline"},
        {"name": "params"},
    ],
)
@fn.controlled_wrapper(
    pybaselines.morphological.amormol, wrapper_attribute="__fnwrapped__"
)
@baselinewrapper
def _amormol(
    data: np.ndarray,
    x_data: Optional[np.ndarray] = None,
    regions: Optional[np.ndarray] = None,
    estimate_window: Optional[float] = None,
    half_window: Optional[int] = None,
    tol: float = 1e-3,
    max_iter: int = 200,
) -> Tuple[np.ndarray, np.ndarray, dict]:
    baseline, params = pybaselines.morphological.amormol(
        data, x_data=x_data, max_iter=max_iter, tol=tol, half_window=half_window
    )
    return baseline, params


@NodeDecorator(
    "pybaselines.morphological.imor",
    name="imor",
    outputs=[
        {"name": "baseline_corrected"},
        {"name": "baseline"},
        {"name": "params"},
    ],
)
@fn.controlled_wrapper(
    pybaselines.morphological.imor, wrapper_attribute="__fnwrapped__"
)
@baselinewrapper
def _imor(
    data: np.ndarray,
    x_data: Optional[np.ndarray] = None,
    regions: Optional[np.ndarray] = None,
    estimate_window: Optional[float] = None,
    half_window: Optional[int] = None,
    tol: float = 1e-3,
    max_iter: int = 200,
) -> Tuple[np.ndarray, np.ndarray, dict]:
    baseline, params = pybaselines.morphological.imor(
        data, x_data=x_data, max_iter=max_iter, tol=tol, half_window=half_window
    )
    return baseline, params


@NodeDecorator(
    "pybaselines.morphological.jbcd",
    name="jbcd",
    outputs=[
        {"name": "baseline_corrected"},
        {"name": "baseline"},
        {"name": "params"},
    ],
)
@fn.controlled_wrapper(
    pybaselines.morphological.jbcd, wrapper_attribute="__fnwrapped__"
)
@baselinewrapper
def _jbcd(
    data: np.ndarray,
    x_data: Optional[np.ndarray] = None,
    regions: Optional[np.ndarray] = None,
    estimate_window: Optional[float] = None,
    half_window: Optional[int] = None,
    alpha: float = 0.1,
    beta: float = 10.0,
    gamma: float = 1.0,
    beta_mult: float = 1.1,
    gamma_mult: float = 0.909,
    diff_order: int = 1,
    tol: float = 1e-2,
    tol_2: float = 1e-3,
    max_iter: int = 20,
    robust_opening: bool = True,
) -> Tuple[np.ndarray, np.ndarray, dict]:
    baseline, params = pybaselines.morphological.jbcd(
        data,
        x_data=x_data,
        max_iter=max_iter,
        tol=tol,
        half_window=half_window,
        alpha=alpha,
        beta=beta,
        gamma=gamma,
        beta_mult=beta_mult,
        gamma_mult=gamma_mult,
        diff_order=diff_order,
        tol_2=tol_2,
        robust_opening=robust_opening,
    )
    return baseline, params


@NodeDecorator(
    "pybaselines.morphological.mor",
    name="mor",
    outputs=[
        {"name": "baseline_corrected"},
        {"name": "baseline"},
        {"name": "params"},
    ],
)
@fn.controlled_wrapper(pybaselines.morphological.mor, wrapper_attribute="__fnwrapped__")
@baselinewrapper
def _mor(
    data: np.ndarray,
    x_data: Optional[np.ndarray] = None,
    regions: Optional[np.ndarray] = None,
    estimate_window: Optional[float] = None,
    half_window: Optional[int] = None,
) -> Tuple[np.ndarray, np.ndarray, dict]:
    baseline, params = pybaselines.morphological.mor(
        data, x_data=x_data, half_window=half_window
    )
    return baseline, params


@NodeDecorator(
    "pybaselines.morphological.mormol",
    name="mormol",
    outputs=[
        {"name": "baseline_corrected"},
        {"name": "baseline"},
        {"name": "params"},
    ],
)
@fn.controlled_wrapper(
    pybaselines.morphological.mormol, wrapper_attribute="__fnwrapped__"
)
@baselinewrapper
def _mormol(
    data: np.ndarray,
    x_data: Optional[np.ndarray] = None,
    regions: Optional[np.ndarray] = None,
    estimate_window: Optional[float] = None,
    half_window: Optional[int] = None,
    tol: float = 1e-3,
    max_iter: int = 200,
    smooth_half_window: Optional[int] = None,
) -> Tuple[np.ndarray, np.ndarray, dict]:
    baseline, params = pybaselines.morphological.mormol(
        data,
        x_data=x_data,
        max_iter=max_iter,
        tol=tol,
        half_window=half_window,
        smooth_half_window=smooth_half_window,
    )
    return baseline, params


@NodeDecorator(
    "pybaselines.morphological.mpls",
    name="mpls",
    outputs=[
        {"name": "baseline_corrected"},
        {"name": "baseline"},
        {"name": "params"},
    ],
)
@fn.controlled_wrapper(
    pybaselines.morphological.mpls, wrapper_attribute="__fnwrapped__"
)
@baselinewrapper
def _mpls(
    data: np.ndarray,
    x_data: Optional[np.ndarray] = None,
    regions: Optional[np.ndarray] = None,
    estimate_window: Optional[float] = None,
    half_window: Optional[int] = None,
    lam: float = 1000000.0,
    p: float = 0.0,
    diff_order: int = 2,
    tol: float = 1e-3,
    max_iter: int = 50,
    weights: Optional[np.ndarray] = None,
) -> Tuple[np.ndarray, np.ndarray, dict]:
    baseline, params = pybaselines.morphological.mpls(
        data,
        x_data=x_data,
        max_iter=max_iter,
        tol=tol,
        half_window=half_window,
        lam=lam,
        p=p,
        diff_order=diff_order,
        weights=weights,
    )
    return baseline, params


@NodeDecorator(
    "pybaselines.morphological.mpspline",
    name="mpspline",
    outputs=[
        {"name": "baseline_corrected"},
        {"name": "baseline"},
        {"name": "params"},
    ],
)
@fn.controlled_wrapper(
    pybaselines.morphological.mpspline, wrapper_attribute="__fnwrapped__"
)
@baselinewrapper
def _mpspline(
    data: np.ndarray,
    x_data: Optional[np.ndarray] = None,
    regions: Optional[np.ndarray] = None,
    estimate_window: Optional[float] = None,
    half_window: Optional[int] = None,
    lam: float = 10000.0,
    lam_smooth: float = 0.01,
    p: float = 0.0,
    num_knots: int = 100,
    spline_degree: int = 3,
    diff_order: int = 2,
    weights: Optional[np.ndarray] = None,
) -> Tuple[np.ndarray, np.ndarray, dict]:
    baseline, params = pybaselines.morphological.mpspline(
        data,
        x_data=x_data,
        half_window=half_window,
        lam=lam,
        lam_smooth=lam_smooth,
        num_knots=num_knots,
        spline_degree=spline_degree,
        p=p,
        diff_order=diff_order,
        weights=weights,
    )
    return baseline, params


@NodeDecorator(
    "pybaselines.morphological.mwmv",
    name="mwmv",
    outputs=[
        {"name": "baseline_corrected"},
        {"name": "baseline"},
        {"name": "params"},
    ],
)
@fn.controlled_wrapper(
    pybaselines.morphological.mwmv, wrapper_attribute="__fnwrapped__"
)
@baselinewrapper
def _mwmv(
    data: np.ndarray,
    x_data: Optional[np.ndarray] = None,
    regions: Optional[np.ndarray] = None,
    estimate_window: Optional[float] = None,
    half_window: Optional[int] = None,
    smooth_half_window: Optional[int] = None,
) -> Tuple[np.ndarray, np.ndarray, dict]:
    baseline, params = pybaselines.morphological.mwmv(
        data,
        x_data=x_data,
        smooth_half_window=smooth_half_window,
        half_window=half_window,
    )
    return baseline, params


@NodeDecorator(
    "pybaselines.morphological.rolling_ball",
    name="rolling_ball",
    outputs=[
        {"name": "baseline_corrected"},
        {"name": "baseline"},
        {"name": "params"},
    ],
)
@fn.controlled_wrapper(
    pybaselines.morphological.rolling_ball, wrapper_attribute="__fnwrapped__"
)
@baselinewrapper
def _rolling_ball(
    data: np.ndarray,
    x_data: Optional[np.ndarray] = None,
    regions: Optional[np.ndarray] = None,
    estimate_window: Optional[float] = None,
    half_window: Optional[int] = None,
    smooth_half_window: Optional[int] = None,
) -> Tuple[np.ndarray, np.ndarray, dict]:
    baseline, params = pybaselines.morphological.rolling_ball(
        data,
        x_data=x_data,
        smooth_half_window=smooth_half_window,
        half_window=half_window,
    )
    return baseline, params


@NodeDecorator(
    "pybaselines.morphological.tophat",
    name="tophat",
    outputs=[
        {"name": "baseline_corrected"},
        {"name": "baseline"},
        {"name": "params"},
    ],
)
@fn.controlled_wrapper(
    pybaselines.morphological.tophat, wrapper_attribute="__fnwrapped__"
)
@baselinewrapper
def _tophat(
    data: np.ndarray,
    x_data: Optional[np.ndarray] = None,
    regions: Optional[np.ndarray] = None,
    estimate_window: Optional[float] = None,
    half_window: Optional[int] = None,
) -> Tuple[np.ndarray, np.ndarray, dict]:
    baseline, params = pybaselines.morphological.tophat(
        data,
        x_data=x_data,
        half_window=half_window,
    )
    return baseline, params


MORPHOLOGICAL_NODE_SHELF = Shelf(
    nodes=[
        _amormol,
        _imor,
        _jbcd,
        _mor,
        _mormol,
        _mpls,
        _mpspline,
        _mwmv,
        _rolling_ball,
        _tophat,
    ],
    subshelves=[],
    name="Morphological",
    description="Fits a morphological baseline",
)


@NodeDecorator(
    "pybaselines.spline.corner_cutting",
    name="corner_cutting",
    outputs=[
        {"name": "baseline_corrected"},
        {"name": "baseline"},
        {"name": "params"},
    ],
)
@fn.controlled_wrapper(
    pybaselines.spline.corner_cutting, wrapper_attribute="__fnwrapped__"
)
@baselinewrapper
def _corner_cutting(
    data: np.ndarray,
    x_data: Optional[np.ndarray] = None,
    regions: Optional[np.ndarray] = None,
    estimate_window: Optional[float] = None,
    max_iter: int = 100,
) -> Tuple[np.ndarray, np.ndarray, dict]:
    baseline, params = pybaselines.spline.corner_cutting(
        data,
        x_data=x_data,
        max_iter=max_iter,
    )
    return baseline, params


@NodeDecorator(
    "pybaselines.spline.irsqr",
    name="irsqr",
    outputs=[
        {"name": "baseline_corrected"},
        {"name": "baseline"},
        {"name": "params"},
    ],
)
@fn.controlled_wrapper(pybaselines.spline.irsqr, wrapper_attribute="__fnwrapped__")
@baselinewrapper
def _irsqr(
    data: np.ndarray,
    x_data: Optional[np.ndarray] = None,
    regions: Optional[np.ndarray] = None,
    estimate_window: Optional[float] = None,
    quantile: float = 0.05,
    num_knots: int = 100,
    spline_degree: int = 3,
    diff_order: int = 3,
    max_iter: int = 100,
    tol: float = 1e-6,
    weights: Optional[np.ndarray] = None,
    eps: Optional[float] = None,
) -> Tuple[np.ndarray, np.ndarray, dict]:
    baseline, params = pybaselines.spline.irsqr(
        data,
        x_data=x_data,
        max_iter=max_iter,
        quantile=quantile,
        num_knots=num_knots,
        spline_degree=spline_degree,
        diff_order=diff_order,
        tol=tol,
        weights=weights,
        eps=eps,
    )
    return baseline, params


@NodeDecorator(
    "pybaselines.spline.mixture_model",
    name="mixture_model",
    outputs=[
        {"name": "baseline_corrected"},
        {"name": "baseline"},
        {"name": "params"},
    ],
)
@fn.controlled_wrapper(
    pybaselines.spline.mixture_model, wrapper_attribute="__fnwrapped__"
)
@baselinewrapper
def _mixture_model(
    data: np.ndarray,
    x_data: Optional[np.ndarray] = None,
    regions: Optional[np.ndarray] = None,
    estimate_window: Optional[float] = None,
    lam: float = 100000.0,
    p: float = 0.01,
    num_knots: int = 100,
    spline_degree: int = 3,
    diff_order: int = 3,
    max_iter: int = 50,
    tol: float = 1e-3,
    weights: Optional[np.ndarray] = None,
    symmetric: bool = False,
    num_bins: Optional[int] = None,
) -> Tuple[np.ndarray, np.ndarray, dict]:
    baseline, params = pybaselines.spline.mixture_model(
        data,
        x_data=x_data,
        max_iter=max_iter,
        lam=lam,
        p=p,
        symmetric=symmetric,
        num_knots=num_knots,
        spline_degree=spline_degree,
        diff_order=diff_order,
        tol=tol,
        weights=weights,
        num_bins=num_bins,
    )
    return baseline, params


@NodeDecorator(
    "pybaselines.spline.pspline_airpls",
    name="pspline_airpls",
    outputs=[
        {"name": "baseline_corrected"},
        {"name": "baseline"},
        {"name": "params"},
    ],
)
@fn.controlled_wrapper(
    pybaselines.spline.pspline_airpls, wrapper_attribute="__fnwrapped__"
)
@baselinewrapper
def _pspline_airpls(
    data: np.ndarray,
    x_data: Optional[np.ndarray] = None,
    regions: Optional[np.ndarray] = None,
    estimate_window: Optional[float] = None,
    lam: float = 1000.0,
    num_knots: int = 100,
    spline_degree: int = 3,
    diff_order: int = 2,
    max_iter: int = 50,
    tol: float = 1e-3,
    weights: Optional[np.ndarray] = None,
) -> Tuple[np.ndarray, np.ndarray, dict]:
    baseline, params = pybaselines.spline.pspline_airpls(
        data,
        x_data=x_data,
        max_iter=max_iter,
        lam=lam,
        num_knots=num_knots,
        spline_degree=spline_degree,
        diff_order=diff_order,
        tol=tol,
        weights=weights,
    )
    return baseline, params


@NodeDecorator(
    "pybaselines.spline.pspline_arpls",
    name="pspline_arpls",
    outputs=[
        {"name": "baseline_corrected"},
        {"name": "baseline"},
        {"name": "params"},
    ],
)
@fn.controlled_wrapper(
    pybaselines.spline.pspline_arpls, wrapper_attribute="__fnwrapped__"
)
@baselinewrapper
def _pspline_arpls(
    data: np.ndarray,
    x_data: Optional[np.ndarray] = None,
    regions: Optional[np.ndarray] = None,
    estimate_window: Optional[float] = None,
    lam: float = 1000.0,
    num_knots: int = 100,
    spline_degree: int = 3,
    diff_order: int = 2,
    max_iter: int = 50,
    tol: float = 1e-3,
    weights: Optional[np.ndarray] = None,
) -> Tuple[np.ndarray, np.ndarray, dict]:
    baseline, params = pybaselines.spline.pspline_arpls(
        data,
        x_data=x_data,
        max_iter=max_iter,
        lam=lam,
        num_knots=num_knots,
        spline_degree=spline_degree,
        diff_order=diff_order,
        tol=tol,
        weights=weights,
    )
    return baseline, params


@NodeDecorator(
    "pybaselines.spline.pspline_asls",
    name="pspline_asls",
    outputs=[
        {"name": "baseline_corrected"},
        {"name": "baseline"},
        {"name": "params"},
    ],
)
@fn.controlled_wrapper(
    pybaselines.spline.pspline_asls, wrapper_attribute="__fnwrapped__"
)
@baselinewrapper
def _pspline_asls(
    data: np.ndarray,
    x_data: Optional[np.ndarray] = None,
    regions: Optional[np.ndarray] = None,
    estimate_window: Optional[float] = None,
    lam: float = 1000.0,
    p: float = 0.01,
    num_knots: int = 100,
    spline_degree: int = 3,
    diff_order: int = 2,
    max_iter: int = 50,
    tol: float = 1e-3,
    weights: Optional[np.ndarray] = None,
) -> Tuple[np.ndarray, np.ndarray, dict]:
    baseline, params = pybaselines.spline.pspline_asls(
        data,
        x_data=x_data,
        max_iter=max_iter,
        lam=lam,
        num_knots=num_knots,
        p=p,
        spline_degree=spline_degree,
        diff_order=diff_order,
        tol=tol,
        weights=weights,
    )
    return baseline, params


@NodeDecorator(
    "pybaselines.spline.pspline_aspls",
    name="pspline_aspls",
    outputs=[
        {"name": "baseline_corrected"},
        {"name": "baseline"},
        {"name": "params"},
    ],
)
@fn.controlled_wrapper(
    pybaselines.spline.pspline_aspls, wrapper_attribute="__fnwrapped__"
)
@baselinewrapper
def _pspline_aspls(
    data: np.ndarray,
    x_data: Optional[np.ndarray] = None,
    regions: Optional[np.ndarray] = None,
    estimate_window: Optional[float] = None,
    lam: float = 10000.0,
    num_knots: int = 100,
    spline_degree: int = 3,
    diff_order: int = 2,
    max_iter: int = 100,
    tol: float = 1e-3,
    weights: Optional[np.ndarray] = None,
    alpha: Optional[np.ndarray] = None,
) -> Tuple[np.ndarray, np.ndarray, dict]:
    baseline, params = pybaselines.spline.pspline_aspls(
        data,
        x_data=x_data,
        max_iter=max_iter,
        lam=lam,
        num_knots=num_knots,
        spline_degree=spline_degree,
        diff_order=diff_order,
        tol=tol,
        weights=weights,
        alpha=alpha,
    )
    return baseline, params


@NodeDecorator(
    "pybaselines.spline.pspline_derpsalsa",
    name="pspline_derpsalsa",
    outputs=[
        {"name": "baseline_corrected"},
        {"name": "baseline"},
        {"name": "params"},
    ],
)
@fn.controlled_wrapper(
    pybaselines.spline.pspline_derpsalsa, wrapper_attribute="__fnwrapped__"
)
@baselinewrapper
def _pspline_derpsalsa(
    data: np.ndarray,
    x_data: Optional[np.ndarray] = None,
    regions: Optional[np.ndarray] = None,
    estimate_window: Optional[float] = None,
    lam: float = 100.0,
    p: float = 0.01,
    k: Optional[float] = None,
    num_knots: int = 100,
    spline_degree: int = 3,
    diff_order: int = 2,
    max_iter: int = 50,
    tol: float = 1e-3,
    weights: Optional[np.ndarray] = None,
    smooth_half_window: Optional[int] = None,
    num_smooths: int = 16,
) -> Tuple[np.ndarray, np.ndarray, dict]:
    baseline, params = pybaselines.spline.pspline_derpsalsa(
        data,
        x_data=x_data,
        max_iter=max_iter,
        lam=lam,
        p=p,
        k=k,
        num_knots=num_knots,
        spline_degree=spline_degree,
        diff_order=diff_order,
        tol=tol,
        weights=weights,
        smooth_half_window=smooth_half_window,
        num_smooths=num_smooths,
    )
    return baseline, params


@NodeDecorator(
    "pybaselines.spline.pspline_drpls",
    name="pspline_drpls",
    outputs=[
        {"name": "baseline_corrected"},
        {"name": "baseline"},
        {"name": "params"},
    ],
)
@fn.controlled_wrapper(
    pybaselines.spline.pspline_drpls, wrapper_attribute="__fnwrapped__"
)
@baselinewrapper
def _pspline_drpls(
    data: np.ndarray,
    x_data: Optional[np.ndarray] = None,
    regions: Optional[np.ndarray] = None,
    estimate_window: Optional[float] = None,
    lam: float = 1000.0,
    eta: float = 0.5,
    num_knots: int = 100,
    spline_degree: int = 3,
    diff_order: int = 2,
    max_iter: int = 50,
    tol: float = 1e-3,
    weights: Optional[np.ndarray] = None,
) -> Tuple[np.ndarray, np.ndarray, dict]:
    baseline, params = pybaselines.spline.pspline_drpls(
        data,
        x_data=x_data,
        max_iter=max_iter,
        lam=lam,
        eta=eta,
        num_knots=num_knots,
        spline_degree=spline_degree,
        diff_order=diff_order,
        tol=tol,
        weights=weights,
    )
    return baseline, params


@NodeDecorator(
    "pybaselines.spline.pspline_iarpls",
    name="pspline_iarpls",
    outputs=[
        {"name": "baseline_corrected"},
        {"name": "baseline"},
        {"name": "params"},
    ],
)
@fn.controlled_wrapper(
    pybaselines.spline.pspline_iarpls, wrapper_attribute="__fnwrapped__"
)
@baselinewrapper
def _pspline_iarpls(
    data: np.ndarray,
    x_data: Optional[np.ndarray] = None,
    regions: Optional[np.ndarray] = None,
    estimate_window: Optional[float] = None,
    lam: float = 1000.0,
    num_knots: int = 100,
    spline_degree: int = 3,
    diff_order: int = 2,
    max_iter: int = 50,
    tol: float = 1e-3,
    weights: Optional[np.ndarray] = None,
) -> Tuple[np.ndarray, np.ndarray, dict]:
    baseline, params = pybaselines.spline.pspline_iarpls(
        data,
        x_data=x_data,
        max_iter=max_iter,
        lam=lam,
        num_knots=num_knots,
        spline_degree=spline_degree,
        diff_order=diff_order,
        tol=tol,
        weights=weights,
    )
    return baseline, params


@NodeDecorator(
    "pybaselines.spline.pspline_iasls",
    name="pspline_iasls",
    outputs=[
        {"name": "baseline_corrected"},
        {"name": "baseline"},
        {"name": "params"},
    ],
)
@fn.controlled_wrapper(
    pybaselines.spline.pspline_iasls, wrapper_attribute="__fnwrapped__"
)
@baselinewrapper
def _pspline_iasls(
    data: np.ndarray,
    x_data: Optional[np.ndarray] = None,
    regions: Optional[np.ndarray] = None,
    estimate_window: Optional[float] = None,
    lam: float = 10.0,
    p: float = 0.01,
    lam_1: float = 0.0001,
    num_knots: int = 100,
    spline_degree: int = 3,
    diff_order: int = 2,
    max_iter: int = 50,
    tol: float = 1e-3,
    weights: Optional[np.ndarray] = None,
) -> Tuple[np.ndarray, np.ndarray, dict]:
    baseline, params = pybaselines.spline.pspline_iasls(
        data,
        x_data=x_data,
        max_iter=max_iter,
        lam=lam,
        p=p,
        lam_1=lam_1,
        num_knots=num_knots,
        spline_degree=spline_degree,
        diff_order=diff_order,
        tol=tol,
        weights=weights,
    )
    return baseline, params


@NodeDecorator(
    "pybaselines.spline.pspline_mpls",
    name="pspline_mpls",
    outputs=[
        {"name": "baseline_corrected"},
        {"name": "baseline"},
        {"name": "params"},
    ],
)
@fn.controlled_wrapper(
    pybaselines.spline.pspline_mpls, wrapper_attribute="__fnwrapped__"
)
@baselinewrapper
def _pspline_mpls(
    data: np.ndarray,
    x_data: Optional[np.ndarray] = None,
    regions: Optional[np.ndarray] = None,
    estimate_window: Optional[float] = None,
    half_window: Optional[int] = None,
    lam: float = 1000.0,
    p: float = 0.0,
    num_knots: int = 100,
    spline_degree: int = 3,
    diff_order: int = 2,
    max_iter: int = 50,
    tol: float = 1e-3,
    weights: Optional[np.ndarray] = None,
) -> Tuple[np.ndarray, np.ndarray, dict]:
    baseline, params = pybaselines.spline.pspline_mpls(
        data,
        x_data=x_data,
        max_iter=max_iter,
        lam=lam,
        p=p,
        half_window=half_window,
        num_knots=num_knots,
        spline_degree=spline_degree,
        diff_order=diff_order,
        tol=tol,
        weights=weights,
    )
    return baseline, params


@NodeDecorator(
    "pybaselines.spline.pspline_psalsa",
    name="pspline_psalsa",
    outputs=[
        {"name": "baseline_corrected"},
        {"name": "baseline"},
        {"name": "params"},
    ],
)
@fn.controlled_wrapper(
    pybaselines.spline.pspline_psalsa, wrapper_attribute="__fnwrapped__"
)
@baselinewrapper
def _pspline_psalsa(
    data: np.ndarray,
    x_data: Optional[np.ndarray] = None,
    regions: Optional[np.ndarray] = None,
    estimate_window: Optional[float] = None,
    lam: float = 1000.0,
    p: float = 0.5,
    k: Optional[float] = None,
    num_knots: int = 100,
    spline_degree: int = 3,
    diff_order: int = 2,
    max_iter: int = 50,
    tol: float = 1e-3,
    weights: Optional[np.ndarray] = None,
) -> Tuple[np.ndarray, np.ndarray, dict]:
    baseline, params = pybaselines.spline.pspline_psalsa(
        data,
        x_data=x_data,
        max_iter=max_iter,
        lam=lam,
        p=p,
        k=k,
        num_knots=num_knots,
        spline_degree=spline_degree,
        diff_order=diff_order,
        tol=tol,
        weights=weights,
    )
    return baseline, params


SPLINE_NODE_SHELF = Shelf(
    nodes=[
        _corner_cutting,
        _irsqr,
        _mixture_model,
        _pspline_airpls,
        _pspline_arpls,
        _pspline_asls,
        _pspline_aspls,
        _pspline_derpsalsa,
        _pspline_drpls,
        _pspline_iarpls,
        _pspline_iasls,
        _pspline_mpls,
        _pspline_psalsa,
    ],
    subshelves=[],
    name="Spline",
    description="Fits a spline baseline",
)


@NodeDecorator(
    "pybaselines.smooth.ipsa",
    name="ipsa",
    outputs=[
        {"name": "baseline_corrected"},
        {"name": "baseline"},
        {"name": "params"},
    ],
)
@fn.controlled_wrapper(pybaselines.smooth.ipsa, wrapper_attribute="__fnwrapped__")
@baselinewrapper
def _ipsa(
    data: np.ndarray,
    x_data: Optional[np.ndarray] = None,
    regions: Optional[np.ndarray] = None,
    estimate_window: Optional[float] = None,
    half_window: Optional[int] = None,
    max_iter: int = 500,
    tol: Optional[float] = None,
    roi: Optional[np.ndarray] = None,
    original_criteria: bool = False,
) -> Tuple[np.ndarray, np.ndarray, dict]:
    baseline, params = pybaselines.smooth.ipsa(
        data,
        x_data=x_data,
        max_iter=max_iter,
        half_window=half_window,
        roi=roi,
        tol=tol,
        original_criteria=original_criteria,
    )
    return baseline, params


@NodeDecorator(
    "pybaselines.smooth.noise_median",
    name="noise_median",
    outputs=[
        {"name": "baseline_corrected"},
        {"name": "baseline"},
        {"name": "params"},
    ],
)
@fn.controlled_wrapper(
    pybaselines.smooth.noise_median, wrapper_attribute="__fnwrapped__"
)
@baselinewrapper
def _noise_median(
    data: np.ndarray,
    x_data: Optional[np.ndarray] = None,
    regions: Optional[np.ndarray] = None,
    estimate_window: Optional[float] = None,
    half_window: Optional[int] = None,
    smooth_half_window: Optional[int] = None,
    sigma: Optional[float] = None,
) -> Tuple[np.ndarray, np.ndarray, dict]:
    baseline, params = pybaselines.smooth.noise_median(
        data,
        x_data=x_data,
        smooth_half_window=smooth_half_window,
        half_window=half_window,
        sigma=sigma,
    )
    return baseline, params


class Side(fn.DataEnum):
    both = "both"
    left = "left"
    right = "right"


@NodeDecorator(
    "pybaselines.smooth.ria",
    name="ria",
    outputs=[
        {"name": "baseline_corrected"},
        {"name": "baseline"},
        {"name": "params"},
    ],
)
@fn.controlled_wrapper(pybaselines.smooth.ria, wrapper_attribute="__fnwrapped__")
@baselinewrapper
def _ria(
    data: np.ndarray,
    x_data: Optional[np.ndarray] = None,
    regions: Optional[np.ndarray] = None,
    estimate_window: Optional[float] = None,
    half_window: Optional[int] = None,
    max_iter: int = 500,
    tol: float = 0.01,
    side: Side = Side.both,
    width_scale: float = 0.1,
    height_scale: float = 1.0,
    sigma_scale: float = 1.0 / 12.0,
) -> Tuple[np.ndarray, np.ndarray, dict]:
    side = Side.v(side)
    baseline, params = pybaselines.smooth.ria(
        data,
        x_data=x_data,
        max_iter=max_iter,
        tol=tol,
        half_window=half_window,
        side=side,
        width_scale=width_scale,
        height_scale=height_scale,
        sigma_scale=sigma_scale,
    )
    return baseline, params


@NodeDecorator(
    "pybaselines.smooth.snip",
    name="snip",
    outputs=[
        {"name": "baseline_corrected"},
        {"name": "baseline"},
        {"name": "params"},
    ],
)
@fn.controlled_wrapper(pybaselines.smooth.snip, wrapper_attribute="__fnwrapped__")
@baselinewrapper
def _snip(
    data: np.ndarray,
    x_data: Optional[np.ndarray] = None,
    regions: Optional[np.ndarray] = None,
    estimate_window: Optional[float] = None,
    decreasing: bool = False,
    smooth_half_window: Optional[int] = None,
    filter_order: int = 2,
) -> Tuple[np.ndarray, np.ndarray, dict]:
    baseline, params = pybaselines.smooth.snip(
        data,
        x_data=x_data,
        decreasing=decreasing,
        smooth_half_window=smooth_half_window,
        filter_order=filter_order,
    )
    return baseline, params


@NodeDecorator(
    "pybaselines.smooth.swima",
    name="swima",
    outputs=[
        {"name": "baseline_corrected"},
        {"name": "baseline"},
        {"name": "params"},
    ],
)
@fn.controlled_wrapper(pybaselines.smooth.swima, wrapper_attribute="__fnwrapped__")
@baselinewrapper
def _swima(
    data: np.ndarray,
    x_data: Optional[np.ndarray] = None,
    regions: Optional[np.ndarray] = None,
    estimate_window: Optional[float] = None,
    min_half_window: int = 3,
    max_half_window: Optional[int] = None,
    smooth_half_window: Optional[int] = None,
) -> Tuple[np.ndarray, np.ndarray, dict]:
    baseline, params = pybaselines.smooth.swima(
        data,
        x_data=x_data,
        min_half_window=min_half_window,
        smooth_half_window=smooth_half_window,
        max_half_window=max_half_window,
    )
    return baseline, params


SMOOTH_NODE_SHELF = Shelf(
    nodes=[_ipsa, _noise_median, _ria, _snip, _swima],
    subshelves=[],
    name="Smooth",
    description="Fits a smooth baseline",
)


@NodeDecorator(
    "pybaselines.classification.cwt_br",
    name="cwt_br",
    outputs=[
        {"name": "baseline_corrected"},
        {"name": "baseline"},
        {"name": "params"},
    ],
)
@fn.controlled_wrapper(
    pybaselines.classification.cwt_br, wrapper_attribute="__fnwrapped__"
)
@baselinewrapper
def _cwt_br(
    data: np.ndarray,
    x_data: Optional[np.ndarray] = None,
    regions: Optional[np.ndarray] = None,
    estimate_window: Optional[float] = None,
    poly_order: int = 5,
    scale: Optional[np.ndarray] = None,
    num_std: float = 1.0,
    min_length: int = 2,
    max_iter: int = 50,
    tol: float = 0.001,
    symmetric: bool = False,
    weights: Optional[np.ndarray] = None,
) -> Tuple[np.ndarray, np.ndarray, dict]:
    baseline, params = pybaselines.classification.cwt_br(
        data,
        x_data=x_data,
        poly_order=poly_order,
        scale=scale,
        num_std=num_std,
        min_length=min_length,
        max_iter=max_iter,
        tol=tol,
        symmetric=symmetric,
        weights=weights,
    )
    return baseline, params


@NodeDecorator(
    "pybaselines.classification.dietrich",
    name="dietrich",
    outputs=[
        {"name": "baseline_corrected"},
        {"name": "baseline"},
        {"name": "params"},
    ],
)
@fn.controlled_wrapper(
    pybaselines.classification.dietrich, wrapper_attribute="__fnwrapped__"
)
@baselinewrapper
def _dietrich(
    data: np.ndarray,
    x_data: Optional[np.ndarray] = None,
    regions: Optional[np.ndarray] = None,
    estimate_window: Optional[float] = None,
    smooth_half_window: Optional[int] = None,
    interp_half_window: int = 5,
    poly_order: int = 5,
    max_iter: int = 50,
    tol: float = 0.001,
    num_std: float = 1.0,
    min_length: int = 2,
    return_coef: bool = False,
    weights: Optional[np.ndarray] = None,
) -> Tuple[np.ndarray, np.ndarray, dict]:
    baseline, params = pybaselines.classification.dietrich(
        data,
        x_data=x_data,
        poly_order=poly_order,
        smooth_half_window=smooth_half_window,
        num_std=num_std,
        min_length=min_length,
        max_iter=max_iter,
        tol=tol,
        interp_half_window=interp_half_window,
        return_coef=return_coef,
        weights=weights,
    )
    return baseline, params


@NodeDecorator(
    "pybaselines.classification.fabc",
    name="fabc",
    outputs=[
        {"name": "baseline_corrected"},
        {"name": "baseline"},
        {"name": "params"},
    ],
)
@fn.controlled_wrapper(
    pybaselines.classification.fabc, wrapper_attribute="__fnwrapped__"
)
@baselinewrapper
def _fabc(
    data: np.ndarray,
    x_data: Optional[np.ndarray] = None,
    regions: Optional[np.ndarray] = None,
    estimate_window: Optional[float] = None,
    lam: float = 1000000.0,
    scale: Optional[np.ndarray] = None,
    num_std: float = 3.0,
    diff_order: int = 2,
    min_length: int = 2,
    weights_as_mask: bool = False,
    weights: Optional[np.ndarray] = None,
) -> Tuple[np.ndarray, np.ndarray, dict]:
    baseline, params = pybaselines.classification.fabc(
        data,
        x_data=x_data,
        lam=lam,
        scale=scale,
        num_std=num_std,
        min_length=min_length,
        diff_order=diff_order,
        weights_as_mask=weights_as_mask,
        weights=weights,
    )
    return baseline, params


@NodeDecorator(
    "pybaselines.classification.fastchrom",
    name="fastchrom",
    outputs=[
        {"name": "baseline_corrected"},
        {"name": "baseline"},
        {"name": "params"},
    ],
)
@fn.controlled_wrapper(
    pybaselines.classification.fastchrom, wrapper_attribute="__fnwrapped__"
)
@baselinewrapper
def _fastchrom(
    data: np.ndarray,
    x_data: Optional[np.ndarray] = None,
    regions: Optional[np.ndarray] = None,
    estimate_window: Optional[float] = None,
    half_window: Optional[int] = None,
    threshold: Optional[float] = None,
    min_fwhm: Optional[int] = None,
    interp_half_window: int = 5,
    smooth_half_window: Optional[int] = None,
    max_iter: int = 100,
    min_length: int = 2,
    weights: Optional[np.ndarray] = None,
) -> Tuple[np.ndarray, np.ndarray, dict]:
    baseline, params = pybaselines.classification.fastchrom(
        data,
        x_data=x_data,
        half_window=half_window,
        threshold=threshold,
        min_fwhm=min_fwhm,
        min_length=min_length,
        max_iter=max_iter,
        smooth_half_window=smooth_half_window,
        interp_half_window=interp_half_window,
        weights=weights,
    )
    return baseline, params


@NodeDecorator(
    "pybaselines.classification.golotvin",
    name="golotvin",
    outputs=[
        {"name": "baseline_corrected"},
        {"name": "baseline"},
        {"name": "params"},
    ],
)
@fn.controlled_wrapper(
    pybaselines.classification.golotvin, wrapper_attribute="__fnwrapped__"
)
@baselinewrapper
def _golotvin(
    data: np.ndarray,
    x_data: Optional[np.ndarray] = None,
    regions: Optional[np.ndarray] = None,
    estimate_window: Optional[float] = None,
    half_window: Optional[int] = None,
    num_std: float = 2.0,
    sections: int = 32,
    threshold: Optional[float] = None,
    interp_half_window: int = 5,
    smooth_half_window: Optional[int] = None,
    min_length: int = 2,
    weights: Optional[np.ndarray] = None,
) -> Tuple[np.ndarray, np.ndarray, dict]:
    baseline, params = pybaselines.classification.golotvin(
        data,
        x_data=x_data,
        half_window=half_window,
        threshold=threshold,
        num_std=num_std,
        min_length=min_length,
        sections=sections,
        smooth_half_window=smooth_half_window,
        interp_half_window=interp_half_window,
        weights=weights,
    )
    return baseline, params


@NodeDecorator(
    "pybaselines.classification.rubberband",
    name="rubberband",
    outputs=[
        {"name": "baseline_corrected"},
        {"name": "baseline"},
        {"name": "params"},
    ],
)
@fn.controlled_wrapper(
    pybaselines.classification.rubberband, wrapper_attribute="__fnwrapped__"
)
@baselinewrapper
def _rubberband(
    data: np.ndarray,
    x_data: Optional[np.ndarray] = None,
    regions: Optional[np.ndarray] = None,
    estimate_window: Optional[float] = None,
    segments: Union[int, np.ndarray] = 1,
    lam: Optional[float] = None,
    diff_order: int = 2,
    smooth_half_window: Optional[int] = None,
    weights: Optional[np.ndarray] = None,
) -> Tuple[np.ndarray, np.ndarray, dict]:
    baseline, params = pybaselines.classification.rubberband(
        data,
        x_data=x_data,
        segments=segments,
        lam=lam,
        diff_order=diff_order,
        smooth_half_window=smooth_half_window,
        weights=weights,
    )
    return baseline, params


@NodeDecorator(
    "pybaselines.classification.std_distribution",
    name="std_distribution",
    outputs=[
        {"name": "baseline_corrected"},
        {"name": "baseline"},
        {"name": "params"},
    ],
)
@fn.controlled_wrapper(
    pybaselines.classification.std_distribution, wrapper_attribute="__fnwrapped__"
)
@baselinewrapper
def _std_distribution(
    data: np.ndarray,
    x_data: Optional[np.ndarray] = None,
    regions: Optional[np.ndarray] = None,
    estimate_window: Optional[float] = None,
    half_window: Optional[int] = None,
    interp_half_window: int = 5,
    fill_half_window: int = 3,
    num_std: float = 1.1,
    smooth_half_window: Optional[int] = None,
    weights: Optional[np.ndarray] = None,
) -> Tuple[np.ndarray, np.ndarray, dict]:
    baseline, params = pybaselines.classification.std_distribution(
        data,
        x_data=x_data,
        half_window=half_window,
        interp_half_window=interp_half_window,
        fill_half_window=fill_half_window,
        smooth_half_window=smooth_half_window,
        num_std=num_std,
        weights=weights,
    )
    return baseline, params


CLASSIFICATION_NODE_SHELF = Shelf(
    nodes=[
        _cwt_br,
        _dietrich,
        _fabc,
        _fastchrom,
        _golotvin,
        _rubberband,
        _std_distribution,
    ],
    subshelves=[],
    name="Classification",
    description="Fits a classification baseline",
)


class Method(fn.DataEnum):
    modpoly = "modpoly"
    imodpoly = "imodpoly"


@NodeDecorator(
    "pybaselines.optimizers.adaptive_minmax",
    name="adaptive_minmax",
    outputs=[
        {"name": "baseline_corrected"},
        {"name": "baseline"},
        {"name": "params"},
    ],
)
@fn.controlled_wrapper(
    pybaselines.optimizers.adaptive_minmax, wrapper_attribute="__fnwrapped__"
)
@baselinewrapper
def _adaptive_minmax(
    data: np.ndarray,
    x_data: Optional[np.ndarray] = None,
    regions: Optional[np.ndarray] = None,
    estimate_window: Optional[float] = None,
    poly_order: Optional[Union[int, List[int]]] = None,
    method: Method = Method.modpoly,
    constrained_fraction: Union[float, List[float]] = 0.01,
    constrained_weight: Union[float, List[float]] = 100000.0,
    estimation_poly_order: int = 2,
    weights: Optional[np.ndarray] = None,
) -> Tuple[np.ndarray, np.ndarray, dict]:
    method = Method.v(method)
    baseline, params = pybaselines.optimizers.adaptive_minmax(
        data,
        x_data=x_data,
        poly_order=poly_order,
        constrained_fraction=constrained_fraction,
        constrained_weight=constrained_weight,
        method=method,
        estimation_poly_order=estimation_poly_order,
        weights=weights,
    )
    return baseline, params


class MethodColab(fn.DataEnum):
    airpls = "airpls"
    arpls = "arpls"
    asls = "asls"
    aspls = "aspls"
    derpsalsa = "derpsalsa"
    drpls = "drpls"
    iarpls = "iarpls"
    iasls = "iasls"
    psalsa = "psalsa"


@NodeDecorator(
    "pybaselines.optimizers.collab_pls",
    name="collab_pls",
    outputs=[
        {"name": "baseline_corrected"},
        {"name": "baseline"},
        {"name": "params"},
    ],
)
@fn.controlled_wrapper(
    pybaselines.optimizers.collab_pls, wrapper_attribute="__fnwrapped__"
)
@baselinewrapper
def _collab_pls(
    data: np.ndarray,
    x_data: Optional[np.ndarray] = None,
    regions: Optional[np.ndarray] = None,
    estimate_window: Optional[float] = None,
    average_dataset: bool = True,
    method: MethodColab = MethodColab.asls,
) -> Tuple[np.ndarray, np.ndarray, dict]:
    method = MethodColab.v(method)
    baseline, params = pybaselines.optimizers.collab_pls(
        data,
        x_data=x_data,
        method=method,
        average_dataset=average_dataset,
    )
    return baseline, params


class MethodAll(fn.DataEnum):
    goldindec = "goldindec"
    imodpoly = "imodpoly"
    loess = "loess"
    modpoly = "modpoly"
    penalizedpoly = "penalizedpoly"
    poly = "poly"
    quant_reg = "quant_reg"
    airpls = "airpls"
    arpls = "arpls"
    asls = "asls"
    aspls = "aspls"
    derpsalsa = "derpsalsa"
    drpls = "drpls"
    iarpls = "iarpls"
    iasls = "iasls"
    psalsa = "psalsa"
    amormol = "amormol"
    imor = "imor"
    jbcd = "jbcd"
    mor = "mor"
    mormol = "mormol"
    mpls = "mpls"
    mpspline = "mpspline"
    mwmv = "mwmv"
    rolling_ball = "rolling_ball"
    tophat = "tophat"
    corner_cutting = "corner_cutting"
    irsqr = "irsqr"
    mixture_model = "mixture_model"
    pspline_airpls = "pspline_airpls"
    pspline_asls = "pspline_asls"
    pspline_aspls = "pspline_aspls"
    pspline_derpsalsa = "pspline_derpsalsa"
    pspline_drpls = "pspline_drpls"
    pspline_iarpls = "pspline_iarpls"
    pspline_iasls = "pspline_iasls"
    pspline_mpls = "pspline_mpls"
    pspline_psalsa = "pspline_psalsa"
    cwt_br = "cwt_br"
    dietrich = "dietrich"
    fabc = "fabc"
    fastchrom = "fastchrom"
    golotvin = "golotvin"
    rubberband = "rubberband"
    std_distribution = "std_distribution"


@NodeDecorator(
    "pybaselines.optimizers.custom_bc",
    name="custom_bc",
    outputs=[
        {"name": "baseline_corrected"},
        {"name": "baseline"},
        {"name": "params"},
    ],
)
@fn.controlled_wrapper(
    pybaselines.optimizers.custom_bc, wrapper_attribute="__fnwrapped__"
)
@baselinewrapper
def _custom_bc(
    data: np.ndarray,
    x_data: Optional[np.ndarray] = None,
    regions: Optional[np.ndarray] = None,
    estimate_window: Optional[float] = None,
    sampling: Union[int, np.ndarray] = 1,
    lam: Optional[float] = None,
    diff_order: int = 2,
    method: MethodAll = MethodAll.asls,
) -> Tuple[np.ndarray, np.ndarray, dict]:
    method = MethodAll.v(method)
    baseline, params = pybaselines.optimizers.custom_bc(
        data,
        x_data=x_data,
        diff_order=diff_order,
        lam=lam,
        method=method,
        sampling=sampling,
    )
    return baseline, params


@NodeDecorator(
    "pybaselines.optimizers.optimize_extended_range",
    name="optimize_extended_range",
    outputs=[
        {"name": "baseline_corrected"},
        {"name": "baseline"},
        {"name": "params"},
    ],
)
@fn.controlled_wrapper(
    pybaselines.optimizers.optimize_extended_range, wrapper_attribute="__fnwrapped__"
)
@baselinewrapper
def _optimize_extended_range(
    data: np.ndarray,
    x_data: Optional[np.ndarray] = None,
    regions: Optional[np.ndarray] = None,
    estimate_window: Optional[float] = None,
    side: Side = Side.both,
    width_scale: float = 0.1,
    height_scale: float = 1.0,
    sigma_scale: float = 1.0 / 12.0,
    min_value: float = 2.0,
    max_value: float = 8.0,
    step: int = 1,
    method: MethodAll = MethodAll.asls,
) -> Tuple[np.ndarray, np.ndarray, dict]:
    method = MethodAll.v(method)
    side = Side.v(side)
    baseline, params = pybaselines.optimizers.optimize_extended_range(
        data,
        x_data=x_data,
        width_scale=width_scale,
        height_scale=height_scale,
        method=method,
        min_value=min_value,
        sigma_scale=sigma_scale,
        max_value=max_value,
        step=step,
    )
    return baseline, params
    return baseline, params


OPTIMIZERS_NODE_SHELF = Shelf(
    nodes=[_adaptive_minmax, _collab_pls, _custom_bc, _optimize_extended_range],
    subshelves=[],
    name="Optimizers",
    description="Fits a optimizers baseline",
)

estimate_baseline_regions_node = fn.NodeDecorator(
    "pybaselines.baseline.estimate_baseline_regions",
    name="Estimate baseline regions",
    outputs=[
        {"name": "baseline"},
        {"name": "is_baseline"},
    ],
)(estimate_baseline_regions)

BASELINE_NODE_SHELF = Shelf(
    nodes=[estimate_baseline_regions_node],
    subshelves=[
        POLYNOMIAL_NODE_SHELF,
        WHITTAKER_NODE_SHELF,
        MORPHOLOGICAL_NODE_SHELF,
        SPLINE_NODE_SHELF,
        SMOOTH_NODE_SHELF,
        CLASSIFICATION_NODE_SHELF,
        OPTIMIZERS_NODE_SHELF,
    ],
    name="Baseline correction",
    description="Provides different techniques for fitting baselines to experimental data using pybaselines.",
)
