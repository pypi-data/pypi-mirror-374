import funcnodes as fn

from .normalization import NORM_NODE_SHELF as NORM
from .smoothing import SMOOTH_NODE_SHELF as SMOOTH
from .peak_analysis import PEAKS_NODE_SHELF as PEAK
from .baseline import BASELINE_NODE_SHELF as BASELINE
from funcnodes_lmfit import NODE_SHELF as LMFIT_NODE_SHELF
from .curves import CURVES_NODE_SHELF

__version__ = "1.0.1"

NODE_SHELF = fn.Shelf(
    name="Spectral Analysis",
    description="Spectral analysis for funcnodes",
    nodes=[],
    subshelves=[NORM, SMOOTH, BASELINE, PEAK, CURVES_NODE_SHELF, LMFIT_NODE_SHELF],
)
