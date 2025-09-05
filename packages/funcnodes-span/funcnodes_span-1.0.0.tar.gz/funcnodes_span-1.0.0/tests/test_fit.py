import unittest
import numpy as np
from lmfit.models import SkewedGaussianModel
from lmfit import CompositeModel
from scipy.ndimage import gaussian_filter1d
from funcnodes_span.peak_analysis import PeakProperties, peak_finder
from funcnodes_span.fitting import (
    fit_peaks,
    group_signals,
)  # Assuming the function is in fit_module.py


class TestFitSignals1D(unittest.TestCase):
    def setUp(self):
        """
        Set up test data for the unit tests. Create a synthetic 1D signal with peaks.
        """
        # Generate synthetic data: a sum of Gaussian peaks with noise
        self.x = np.linspace(0, 100, 500)
        self.rnd = np.random.RandomState(42)
        self.y = (
            10 * np.exp(-((self.x - 20) ** 2) / (2 * 2**2))  # Peak 1
            + 5 * np.exp(-((self.x - 30) ** 2) / (2 * 5**2))  # Peak 2
            + 7 * np.exp(-((self.x - 80) ** 2) / (2 * 3**2))  # Peak 3
        ) + self.rnd.normal(0, 0.2, self.x.size)  # Add some noise

        self.peaks, _, _ = peak_finder.o_func(
            gaussian_filter1d(self.y, 5),
            self.x,
        )

        self.assertEqual(
            len(self.peaks),
            3,
            "Incorrect number of peaks detected in the synthetic data.",
        )

    def test_group_signals(self):
        res = group_signals(self.x, self.y, self.peaks)
        self.assertEqual(
            len(res),
            2,
            "Incorrect number of groups detected in the synthetic data.",
        )

        self.assertEqual(
            len(res[0]),
            2,
            "Incorrect number of peaks in the first group.",
        )

        self.assertEqual(
            len(res[1]),
            1,
            "Incorrect number of peaks in the second group.",
        )

    def test_fit_signals_1D_default(self):
        """
        Test fit_signals_1D with default settings.
        Ensure that the returned model fits the synthetic data properly.
        """
        fitted_peaks, model, result = fit_peaks(self.peaks, self.x, self.y)

        # Check the type of the returned model
        self.assertIsInstance(
            model, CompositeModel, "Model is not of the expected type."
        )

        submodels = model.components
        self.assertEqual(
            len(submodels),
            3,
            "Incorrect number of submodels in the composite model.",
        )

        # Check that the model is not None
        self.assertIsNotNone(model, "The fitted model is None.")

        # Fit the global model to data and check that it improves fit

        self.assertTrue(result.success, "Fitting process failed.")
        self.assertGreater(
            result.rsquared,
            0.99,
            "R-squared value is too low for the fitted model.",
        )

    def test_fit_signals_1D_incomplete_peak_handling(self):
        """
        Test that the function handles incomplete peaks correctly by extending x-range.
        In this case, peaks at the boundaries should be handled by extending the range.
        """
        # Manually truncate the first and last peaks
        self.peaks[0] = PeakProperties(
            id=self.peaks[0].id,
            i_index=self.peaks[0].index,
            index=self.peaks[0].index,
            f_index=self.peaks[0].f_index,
            yfull=self.peaks[0].yfull,
            xfull=self.peaks[0].xfull,
        )
        fitted_peaks, model, result = fit_peaks(
            self.peaks,
            self.x,
            self.y,
            incomplete_threshold=0.8,
            incomplete_x_extend=2.0,
        )

        # Ensure the model was created and fitted
        self.assertIsNotNone(
            model, "Model is None, indicating an issue with incomplete peak handling."
        )
        self.assertTrue(result.success, "Fitting failed for incomplete peak.")
        self.assertGreater(
            result.params["p1_center"].value,
            0,
            "Center of incomplete peak is incorrect.",
        )
        self.assertGreater(
            result.rsquared,
            0.99,
            "R-squared value is too low for the fitted model.",
        )

    def test_fit_signals_1D_no_peaks(self):
        """
        Test the behavior when no peaks are provided.
        The function should handle empty peak lists gracefully.
        """
        empty_peaks = []
        with self.assertRaises(ValueError):
            fitted_peaks, model, result = fit_peaks(empty_peaks, self.x, self.y)

    def test_fit_signals_1D_negative_y_handling(self):
        """
        Test the handling of negative y-values. The function should filter them out if filter_negatives is True.
        """
        # Modify data to have negative y-values
        self.y -= 0.2
        self.peaks, _, _ = peak_finder.o_func(
            gaussian_filter1d(self.y, 5),
            self.x,
        )
        fitted_peaks, model, result = fit_peaks(
            self.peaks, self.x, self.y, filter_negatives=True
        )

        # Ensure the model is created and fit successfully despite negative y-values
        self.assertIsNotNone(model, "Model is None with negative y-values.")
        self.assertTrue(
            result.success, "Fitting process failed with negative y-values."
        )

        # Ensure negative values were filtered
        filtered_y = self.y[self.y >= 0]
        self.assertTrue(
            len(filtered_y) < len(self.y),
            "Negative values were not filtered out as expected.",
        )

    def test_fit_signals_1D_custom_model_class(self):
        """
        Test the fitting process with a custom model class instead of the default SkewedGaussianModel.
        """
        fitted_peaks, model, result = fit_peaks(
            self.peaks, self.x, self.y, model_class=SkewedGaussianModel
        )

        # Check that the model was created using the Gaussian model
        self.assertIsInstance(
            model, CompositeModel, "Custom model class was not used as expected."
        )

        # Perform the fit and check if the fit is successful
        self.assertTrue(result.success, "Fitting failed with custom model class.")
        self.assertGreaterEqual(
            result.rsquared,
            0.99,
            f"R-squared value {result.rsquared} is too low for the fitted model.",
        )
