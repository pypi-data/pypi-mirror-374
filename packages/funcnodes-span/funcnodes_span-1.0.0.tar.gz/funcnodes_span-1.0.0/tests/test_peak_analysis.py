import funcnodes as fn
import unittest
import numpy as np
from funcnodes_span.peak_analysis import (
    peak_finder,
    PeakProperties,
    interpolation_1d,
    fit_peaks_node,
    plot_peaks,
    plot_peak,
    plot_fitted_peaks,
    force_peak_finder,
    peaks_from_fitted_node,
    fit_peak_node,
)
from scipy.datasets import electrocardiogram
import plotly.graph_objects as go
from funcnodes_basic.lists import list_get

fn.config.IN_NODE_TEST = True


class TestPeakFinder(unittest.IsolatedAsyncioTestCase):
    async def test_default(self):
        peaks: fn.Node = peak_finder()
        peaks.inputs["y"].value = electrocardiogram()[2000:4000]
        peaks.inputs["x"].value = np.arange(len(electrocardiogram()[2000:4000]))
        peaks.inputs["height"].value = 2
        self.assertIsInstance(peaks, fn.Node)
        await peaks
        out = peaks.outputs["peaks"]
        self.assertIsInstance(out.value[0], PeakProperties)
        self.assertEqual(len(out.value), 1)

    async def test_plot_peaks(self):
        peaks: fn.Node = peak_finder()
        peaks.inputs["y"].value = electrocardiogram()[2000:4000]
        peaks.inputs["x"].value = np.arange(len(electrocardiogram()[2000:4000]))
        peaks.inputs["height"].value = 2

        plotter = plot_peaks()

        plotter.inputs["peaks"].connect(peaks.outputs["peaks"])
        plotter.inputs["y"].value = electrocardiogram()[2000:4000]
        plotter.inputs["x"].value = np.arange(len(electrocardiogram()[2000:4000]))

        await fn.run_until_complete(peaks, plotter)

        self.assertIsInstance(plotter.outputs["figure"].value, go.Figure)

    async def test_plot_peak(self):
        peaks: fn.Node = peak_finder()
        peaks.inputs["y"].value = electrocardiogram()[2000:4000]
        peaks.inputs["x"].value = np.arange(len(electrocardiogram()[2000:4000]))
        peaks.inputs["height"].value = 2

        idxnode = list_get()
        idxnode.inputs["index"].value = 0
        idxnode.inputs["lst"].connect(peaks.outputs["peaks"])

        plotter = plot_peak()

        plotter.inputs["peak"].connect(idxnode.outputs["element"])
        print("AAA",peaks.inputs["y"].is_connected(),plotter.inputs["y"].is_connected())
        plotter.inputs["y"].forwards_from(peaks.inputs["y"])
        plotter.inputs["x"].forwards_from(peaks.inputs["x"])

        await fn.run_until_complete(peaks, plotter, idxnode)

        self.assertIsInstance(plotter.outputs["figure"].value, go.Figure)

    async def test_peak_finder_annotations(self):
        n = peak_finder()
        assert n["on"].hidden


class TestInterpolation(unittest.IsolatedAsyncioTestCase):
    async def test_default(self):
        inter1d: fn.Node = interpolation_1d()
        inter1d.inputs["y"].value = electrocardiogram()[2000:4000]
        inter1d.inputs["x"].value = np.arange(len(electrocardiogram()[2000:4000]))
        inter1d.inputs["multipled_by"].value = 2
        self.assertIsInstance(inter1d, fn.Node)
        await inter1d
        y_interpolated = inter1d.outputs["y_interpolated"]
        x_interpolated = inter1d.outputs["x_interpolated"]
        self.assertIsInstance(y_interpolated.value, np.ndarray)
        self.assertIsInstance(x_interpolated.value, np.ndarray)
        self.assertEqual(
            len(y_interpolated.value), 2 * len(electrocardiogram()[2000:4000])
        )


class TestFit1D(unittest.IsolatedAsyncioTestCase):
    async def test_default(self):
        peaks: fn.Node = peak_finder()
        peaks.inputs["y"].value = electrocardiogram()[2000:4000]
        peaks.inputs["x"].value = np.arange(len(electrocardiogram()[2000:4000]))
        peaks.inputs["height"].value = 2
        self.assertIsInstance(peaks, fn.Node)
        await peaks
        self.assertIsInstance(peaks.outputs["peaks"].value[0], PeakProperties)
        fit: fn.Node = fit_peaks_node()
        fit.inputs["y"].value = electrocardiogram()[2000:4000]
        fit.inputs["x"].value = np.arange(len(electrocardiogram()[2000:4000]))
        fit.inputs["peaks"].connect(peaks.outputs["peaks"])

        self.assertIsInstance(fit, fn.Node)
        await fit
        fitted_peaks = fit.outputs["fitted_peaks"]
        self.assertIsInstance(fitted_peaks.value[0], PeakProperties)

    async def test_fit_wo_baseline(self):
        peaks: fn.Node = peak_finder()
        peaks.inputs["y"].value = electrocardiogram()[2000:4000]
        peaks.inputs["x"].value = np.arange(len(electrocardiogram()[2000:4000]))
        peaks.inputs["height"].value = 2
        self.assertIsInstance(peaks, fn.Node)
        await peaks
        self.assertIsInstance(peaks.outputs["peaks"].value[0], PeakProperties)
        fit: fn.Node = fit_peaks_node()
        fit.inputs["y"].value = electrocardiogram()[2000:4000]
        fit.inputs["x"].value = np.arange(len(electrocardiogram()[2000:4000]))
        fit.inputs["peaks"].connect(peaks.outputs["peaks"])

        self.assertIsInstance(fit, fn.Node)

        await fn.run_until_complete(fit, peaks)
        out = fit.outputs["fitted_peaks"]
        self.assertIsInstance(out.value[0], PeakProperties)

    async def test_plot_fitted_peaks(self):
        peaks: fn.Node = peak_finder()
        peaks.inputs["y"].value = electrocardiogram()[2000:4000]
        peaks.inputs["x"].value = np.arange(len(electrocardiogram()[2000:4000]))
        peaks.inputs["height"].value = 2

        fit: fn.Node = fit_peaks_node()
        fit.inputs["y"].value = electrocardiogram()[2000:4000]
        fit.inputs["x"].value = np.arange(len(electrocardiogram()[2000:4000]))
        fit.inputs["peaks"].connect(peaks.outputs["peaks"])

        plotter = plot_fitted_peaks()

        plotter.inputs["peaks"].connect(fit.outputs["fitted_peaks"])

        await fn.run_until_complete(fit, peaks, plotter)

        self.assertIsInstance(plotter.outputs["figure"].value, go.Figure)


class TestForcePeakFinder(unittest.IsolatedAsyncioTestCase):
    async def test_force_peak_finder(self):
        x = np.linspace(0, 20, 1000)
        # gaussian distribution
        y = np.exp(-((x - 10) ** 2)) + np.exp(-(((x - 12) / 3) ** 2))
        peaks: fn.Node = peak_finder()
        peaks.inputs["y"].value = y
        peaks.inputs["x"].value = x

        await peaks

        force_peaks: fn.Node = force_peak_finder()

        force_peaks.inputs["basic_peak"].value = peaks.outputs["peaks"].value[0]

        force_peaks.inputs["y"].value = y
        force_peaks.inputs["x"].value = x

        await force_peaks

        self.assertIsInstance(force_peaks.outputs["out"].value[0], PeakProperties)
        self.assertEqual(len(force_peaks.outputs["out"].value), 2)

        fit_peaks = fit_peaks_node()
        fit_peaks.inputs["y"].value = y
        fit_peaks.inputs["x"].value = x
        fit_peaks.inputs["peaks"].connect(force_peaks.outputs["out"])

        await fit_peaks

        self.assertIsInstance(
            fit_peaks.outputs["fitted_peaks"].value[0], PeakProperties
        )

    async def test_fit_peak_node(self):
        node = fit_peak_node()
        x = np.linspace(0, 20, 1000)
        # gaussian distribution
        y = np.exp(-((x - 10) ** 2))
        node.inputs["y"].value = y
        node.inputs["x"].value = x
        node.inputs["peak"].value = PeakProperties("p1", 250, 450, 750)

        await node

        self.assertIsInstance(node.outputs["fitted_peak"].value, PeakProperties)
        self.assertEqual(
            node.outputs["model"].value.make_params()["pp1_center"].value,
            10,
            node.outputs["model"].value.make_params(),
        )

    async def test_peaks_from_fitted(self):
        peaks: fn.Node = peak_finder()
        peaks.inputs["y"].value = electrocardiogram()[2000:4000]
        peaks.inputs["x"].value = np.arange(len(electrocardiogram()[2000:4000]))
        peaks.inputs["height"].value = 2
        self.assertIsInstance(peaks, fn.Node)
        await peaks
        self.assertIsInstance(peaks.outputs["peaks"].value[0], PeakProperties)
        fit: fn.Node = fit_peaks_node()
        fit.inputs["y"].value = electrocardiogram()[2000:4000]
        fit.inputs["x"].value = np.arange(len(electrocardiogram()[2000:4000]))
        fit.inputs["peaks"].connect(peaks.outputs["peaks"])

        self.assertIsInstance(fit, fn.Node)
        await fit
        fitted_peaks = fit.outputs["fitted_peaks"]
        self.assertIsInstance(fitted_peaks.value[0], PeakProperties)

        _peaks_from_fitted_node = peaks_from_fitted_node()
        _peaks_from_fitted_node.inputs["fitted_peaks"].connect(
            fit.outputs["fitted_peaks"]
        )

        await _peaks_from_fitted_node

        self.assertIsInstance(
            _peaks_from_fitted_node.outputs["peaks"].value[0], PeakProperties
        )
