from typing import Dict, Optional, Literal, Any, Tuple
from exposedfunctionality import add_type
import numpy as np
from scipy import integrate
from scipy.stats import skew
from lmfit.model import Model


class PeakProperties:
    def __init__(
        self,
        id: str,
        i_index: int,
        index: int,
        f_index: int,
        xfull: Optional[np.ndarray] = None,
        yfull: Optional[np.ndarray] = None,
        **properties,
    ):
        self._id = id
        self._i_index = int(i_index)
        self._index = int(index)
        self._f_index = int(f_index)

        if self._i_index < 0 or self._index < 0 or self._f_index < 0:
            raise ValueError("The indices must be non-negative")

        self._tempx: Optional[np.ndarray] = None
        self._tempy: Optional[np.ndarray] = None

        if not self._i_index <= self._index <= self._f_index:
            raise ValueError(
                "The peak maximum index is not between the starting and ending indices"
            )

        if xfull is not None:
            self.xfull = xfull
        if yfull is not None:
            self.yfull = yfull

        self._model: Optional[Model] = None

        self._serdata = {}

        for key, value in properties.items():
            self.add_serializable_property(key, value)

    def add_serializable_property(self, key: str, value: Any) -> None:
        self._serdata[key] = value

    def __getattribute__(self, name):
        if name.startswith("_"):
            return super().__getattribute__(name)
        try:
            return super().__getattribute__(name)
        except AttributeError as e:
            if name in self._serdata:
                return self._serdata[name]
            else:
                raise e

    @property
    def positive(self) -> bool:
        return (
            self.y_at_index >= self.y_at_i_index
            and self.y_at_index >= self.y_at_f_index
        )

    @property
    def i_index(self) -> int:
        return self._i_index

    @property
    def index(self) -> int:
        return self._index

    @property
    def f_index(self) -> int:
        return self._f_index

    @property
    def id(self) -> str:
        return self._id

    @property
    def xfull(self) -> Optional[np.ndarray]:
        return self._tempx.copy() if self._tempx is not None else None

    @xfull.setter
    def xfull(self, x: np.ndarray) -> None:
        if self._tempx is not None:
            raise ValueError("The full x-array has already been set")
        if self._tempy is not None:
            if len(x) != len(self._tempy):
                raise ValueError(
                    f"The full x-array [{len(x)}] must have the same length as the full y-array [{len(self._tempy)}]"
                )

        if len(x) < self._f_index + 1:
            raise ValueError(
                f"The full x-array [{len(x)}] must have at least f_index + 1 elements ({self._f_index + 1})"
            )

        self._tempx = x.copy()

        if not self.x_at_i_index <= self.x_at_index <= self.x_at_f_index:
            self._tempx = None
            raise ValueError(
                "The peak maximum is not between the starting and ending x-values"
            )

    @property
    def yfull(self) -> Optional[np.ndarray]:
        return self._tempy.copy() if self._tempy is not None else None

    @yfull.setter
    def yfull(self, y: np.ndarray) -> None:
        if self._tempy is not None:
            raise ValueError("The full y-array has already been set")
        if self._tempx is not None:
            if len(y) != len(self._tempx):
                raise ValueError(
                    f"The full y-array [{len(y)}] must have the same length as the full x-array [{len(self._tempx)}]"
                )

        if len(y) < self._f_index + 1:
            raise ValueError(
                f"The full y-array [{len(y)}] must have at least f_index + 1 elements ({self._f_index + 1})"
            )

        self._tempy = y.copy()

        # The following has to be removed because it is not working with "shoulder" peaks
        # if self.y_at_index < self.y_at_i_index and self.y_at_index > self.y_at_f_index:
        #     self._tempy = None
        #     raise ValueError(
        #         "The peak maximum is below the starting but above the ending value"
        #     )
        # elif (
        #     self.y_at_index > self.y_at_i_index and self.y_at_index < self.y_at_f_index
        # ):
        #     self._tempy = None
        #     raise ValueError(
        #         "The peak maximum is above the starting but below the ending value"
        #     )

    @property
    def xrange(self) -> Optional[np.ndarray]:
        if self._tempx is None:
            return None
        return self._tempx[self._i_index : self._f_index + 1].copy()

    @property
    def yrange(self) -> Optional[np.ndarray]:
        if self._tempy is None:
            return None
        return self._tempy[self._i_index : self._f_index + 1].copy()

    @property
    def yrange_corrected(self) -> Optional[np.ndarray]:
        # substract baseline
        yr = self.yrange
        xr = self.xrange
        if yr is None or xr is None:
            return None
        m: float = (yr[-1] - yr[0]) / (xr[-1] - xr[0])
        b: float = yr[0] - m * xr[0]
        return yr - (m * xr + b)

    @property
    def x_at_i_index(self) -> float:
        if self._tempx is None:
            raise ValueError("The full x-array has not been set")
        return self._tempx[self._i_index]

    @property
    def x_at_index(self) -> float:
        if self._tempx is None:
            raise ValueError("The full x-array has not been set")
        return self._tempx[self._index]

    @property
    def x_at_f_index(self) -> float:
        if self._tempx is None:
            raise ValueError("The full x-array has not been set")
        return self._tempx[self._f_index]

    @property
    def y_at_i_index(self) -> float:
        if self._tempy is None:
            raise ValueError("The full y-array has not been set")
        return self._tempy[self._i_index]

    @property
    def y_at_index(self) -> float:
        if self._tempy is None:
            raise ValueError("The full y-array has not been set")
        return self._tempy[self._index]

    @property
    def y_at_f_index(self) -> float:
        if self._tempy is None:
            raise ValueError("The full y-array has not been set")
        return self._tempy[self._f_index]

    @property
    def model(self) -> Optional[Model]:
        return self._model

    @model.setter
    def model(self, model: Model) -> None:
        self._model = model

    def get_width_at_height(
        self, height: float, corrected=False, absolute=True
    ) -> Tuple[float, float, float, float, float, float]:
        """
        Calculate the width of the peak at a given height.

        Args:
            height (float): The height at which to calculate the width.
            corrected (bool): Whether to use the baseline-corrected data. Defaults to False.

        Returns:
            Tuple[float, float, float, float, float, float]: The full, left and right width of the peak at the
            specified height, the absolute height and left and right x.
        """

        if height < 0 or height > 1:
            raise ValueError("The height must be between 0 and 1")

        if corrected:
            y = np.abs(self.yrange_corrected)
        else:
            y = np.abs(self.yrange)

        x = self.xrange

        if y is None or x is None:
            raise ValueError("The full x or y array has not been set")

        if absolute:
            miny = 0
        else:
            miny = min(y[0], y[-1])

        absheight = miny + height * (y[self.index - self.i_index] - miny)

        # Find the first index on the left and right where y > height
        larger_indices = np.where(y >= absheight)[0]

        if len(larger_indices) == 0:
            raise ValueError("No data points exceed the specified height")

        x_at_index = self.x_at_index
        left_x = x[larger_indices[0]]
        right_x = x[larger_indices[-1]]

        return (
            right_x - left_x,
            x_at_index - left_x,
            right_x - x_at_index,
            absheight,
            left_x,
            right_x,
        )

    @property
    def fwhm(self) -> float:
        return self.get_width_at_height(0.5)[0]

    @property
    def width_base(self) -> float:
        return self.x_at_f_index - self.x_at_i_index

    def __str__(self):
        return f"PeakProperties(id={self._id}, i_index={self._i_index}, index={self._index}, f_index={self._f_index})"

    def to_dict(self, calc_props=True) -> Dict[str, Any]:
        if calc_props:
            if not hasattr(self, "area"):
                calculate_peak_area(self, add_property=True)
            if not hasattr(self, "symmetricity"):
                calculate_peak_symmetricity(self, add_property=True)
        return {
            "id": self.id,
            "i_index": self.i_index,
            "index": self.index,
            "f_index": self.f_index,
            "x_at_i_index": self.x_at_i_index,
            "x_at_index": self.x_at_index,
            "x_at_f_index": self.x_at_f_index,
            "y_at_i_index": self.y_at_i_index,
            "y_at_index": self.y_at_index,
            "y_at_f_index": self.y_at_f_index,
            **self._serdata,
        }


add_type(PeakProperties, "PeakProperties")


def calculate_peak_area(
    peak: PeakProperties,
    method: Literal["trapz", "simps"] = "trapz",
    absolute: bool = False,
    relative_to_baseline: bool = False,
    add_property: bool = True,
) -> float:
    """
    Calculate the area under a peak using the specified method.

    Args:
        peak (PeakProperties): The peak properties.
        method (str): The method to use for integration. Defaults to "trapz".
        absolute (bool): Whether to calculate the absolute area (positive values). Defaults to False.
        relative_to_baseline (bool): Whether to calculate the area relative to the baseline
                                     connecting the start and end of the peak. Defaults to False.

    Returns:
        float: The area under the peak.
    """
    yr = peak.yrange
    xr = peak.xrange

    if relative_to_baseline:
        yr = peak.yrange_corrected

    if yr is None:
        raise ValueError("The full y-array has not been set")
    if xr is None:
        raise ValueError("The full x-array has not been set")

    if not peak.positive and not absolute:
        yr = -yr

    if absolute:
        yr = np.abs(yr)

    if method == "trapz":
        area = integrate.trapezoid(yr, xr)
    elif method == "simps":
        area = integrate.simpson(yr, xr)

    else:
        raise ValueError(f"Unsupported method: {method}")

    # Adjust area sign if peak is negative
    if not peak.positive and not absolute:
        area = -area

    if add_property:
        peak.add_serializable_property("area", area)

    return area


def calculate_peak_symmetricity(
    peak: PeakProperties,
    method: Literal["area", "area_simps", "h5p", "fwhm", "skewness"] = "area",
    add_property: bool = True,
) -> float:
    yr = peak.yrange_corrected
    xr = peak.xrange

    if yr is None or xr is None:
        raise ValueError("The full x or y array has not been set")

    yr = np.abs(yr)

    # Split the data into left and right halves around the peak index
    peak_index = peak._index
    x_left = xr[: peak_index + 1]  # Includes the peak index
    y_left = yr[: peak_index + 1]  # Includes the peak index
    x_right = xr[peak_index:]  # Includes the peak index
    y_right = yr[peak_index:]  # Includes the peak index

    if method in ["area", "area_trapz"]:
        # Calculate the area of the left and right halves of the peak
        left_area = integrate.trapezoid(y_left, x=x_left)
        right_area = integrate.trapezoid(y_right, x=x_right)
        # Calculate the symmetricity as the ratio of the smaller area to the larger area
        symmetricity = min(left_area, right_area) / max(left_area, right_area)
    elif method == "area_simps":
        # Calculate the area of the left and right halves of the peak
        left_area = integrate.simpson(y_left, x=x_left)
        right_area = integrate.simpson(y_right, x=x_right)
        # Calculate the symmetricity as the ratio of the smaller area to the larger area
        symmetricity = min(left_area, right_area) / max(left_area, right_area)

    elif method in ["h5p", "fwhm"]:
        if method == "h5p":
            f = 0.05
        elif method == "fwhm":
            f = 0.5

        total_w, left_w, right_w, _, _, _ = peak.get_width_at_height(f)
        symmetricity = max(left_w, right_w) / min(left_w, right_w)

    elif method == "skewness":
        # Statistical skewness method
        xr_diff = np.diff(xr)
        if not np.allclose(xr_diff, xr_diff[0]):
            xrn = np.linspace(xr[0], xr[-1], len(xr))
            yrn = np.interp(xrn, xr, yr)
            yr = yrn
            xr = xrn
        symmetricity = skew(yr)
    else:
        raise ValueError(f"Unsupported method: {method}")

    # Optionally store the symmetricity as a serializable property
    if add_property:
        peak.add_serializable_property("symmetricity", symmetricity)

    return symmetricity
