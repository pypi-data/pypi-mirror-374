import numpy as np
from pybaselines.utils import gaussian
import funcnodes as fn
import unittest
from funcnodes_span.baseline import (
    _goldindec,
    _imodpoly,
    _loess,
    _modpoly,
    _penalized_poly,
    _poly,
    _quant_reg,
    _airpls,
    _arpls,
    _asls,
    _aspls,
    _derpsalsa,
    _drpls,
    _iarpls,
    _iasls,
    _psalsa,
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
    _ipsa,
    _noise_median,
    _ria,
    _snip,
    _swima,
    _cwt_br,
    _dietrich,
    _fabc,
    _fastchrom,
    _golotvin,
    _rubberband,
    _std_distribution,
    _adaptive_minmax,
    _collab_pls,
    _custom_bc,
    _optimize_extended_range,
    estimate_baseline_regions_node,
    flatfit,
)


x = np.linspace(0, 1000, 1000)
signal = (
    gaussian(x, 9, 100, 12)
    + gaussian(x, 6, 180, 5)
    + gaussian(x, 8, 350, 11)
    + gaussian(x, 15, 400, 18)
    + gaussian(x, 6, 550, 6)
    + gaussian(x, 13, 700, 8)
    + gaussian(x, 9, 800, 9)
    + gaussian(x, 9, 880, 7)
)
baseline = 5 + 10 * np.exp(-x / 600)

noise = np.random.RandomState(42).normal(0, 0.1, len(x))
y = signal + baseline + noise


class TestBaselinePolynomial(unittest.IsolatedAsyncioTestCase):
    async def test_goldindec(self):
        bl: fn.Node = _goldindec()
        bl.inputs["data"].value = y
        bl.inputs["poly_order"].value = 3
        self.assertIsInstance(bl, fn.Node)
        await bl
        baseline_corrected = bl.outputs["baseline_corrected"]
        baseline = bl.outputs["baseline"]
        params = bl.outputs["params"]
        self.assertIsInstance(baseline_corrected.value, np.ndarray)
        self.assertIsInstance(baseline.value, np.ndarray)
        self.assertIsInstance(params.value, dict)

    async def test_imodpoly(self):
        bl: fn.Node = _imodpoly()
        bl.inputs["data"].value = y
        bl.inputs["poly_order"].value = 3
        self.assertIsInstance(bl, fn.Node)
        await bl
        baseline_corrected = bl.outputs["baseline_corrected"]
        baseline = bl.outputs["baseline"]
        params = bl.outputs["params"]
        self.assertIsInstance(baseline_corrected.value, np.ndarray)
        self.assertIsInstance(baseline.value, np.ndarray)
        self.assertIsInstance(params.value, dict)

    async def test_loess(self):
        bl: fn.Node = _loess()
        bl.inputs["data"].value = y
        bl.inputs["poly_order"].value = 3
        self.assertIsInstance(bl, fn.Node)
        await bl
        baseline_corrected = bl.outputs["baseline_corrected"]
        baseline = bl.outputs["baseline"]
        params = bl.outputs["params"]
        self.assertIsInstance(baseline_corrected.value, np.ndarray)
        self.assertIsInstance(baseline.value, np.ndarray)
        self.assertIsInstance(params.value, dict)

    async def test_modpoly(self):
        bl: fn.Node = _modpoly()
        bl.inputs["data"].value = y
        bl.inputs["poly_order"].value = 3
        self.assertIsInstance(bl, fn.Node)
        await bl
        baseline_corrected = bl.outputs["baseline_corrected"]
        baseline = bl.outputs["baseline"]
        params = bl.outputs["params"]
        self.assertIsInstance(baseline_corrected.value, np.ndarray)
        self.assertIsInstance(baseline.value, np.ndarray)
        self.assertIsInstance(params.value, dict)

    async def test_penalized_poly(self):
        bl: fn.Node = _penalized_poly()
        bl.inputs["data"].value = y
        bl.inputs["poly_order"].value = 3
        self.assertIsInstance(bl, fn.Node)
        await bl
        baseline_corrected = bl.outputs["baseline_corrected"]
        baseline = bl.outputs["baseline"]
        params = bl.outputs["params"]
        self.assertIsInstance(baseline_corrected.value, np.ndarray)
        self.assertIsInstance(baseline.value, np.ndarray)
        self.assertIsInstance(params.value, dict)

    async def test_poly(self):
        bl: fn.Node = _poly()
        bl.inputs["data"].value = y
        bl.inputs["poly_order"].value = 3
        self.assertIsInstance(bl, fn.Node)
        await bl
        baseline_corrected = bl.outputs["baseline_corrected"]
        baseline = bl.outputs["baseline"]
        params = bl.outputs["params"]
        self.assertIsInstance(baseline_corrected.value, np.ndarray)
        self.assertIsInstance(baseline.value, np.ndarray)
        self.assertIsInstance(params.value, dict)

    async def test_quant_reg(self):
        bl: fn.Node = _quant_reg()
        bl.inputs["data"].value = y
        bl.inputs["poly_order"].value = 3
        self.assertIsInstance(bl, fn.Node)
        await bl
        baseline_corrected = bl.outputs["baseline_corrected"]
        baseline = bl.outputs["baseline"]
        params = bl.outputs["params"]
        self.assertIsInstance(baseline_corrected.value, np.ndarray)
        self.assertIsInstance(baseline.value, np.ndarray)
        self.assertIsInstance(params.value, dict)


class TestBaselineWhittaker(unittest.IsolatedAsyncioTestCase):
    async def test_airpls(self):
        bl: fn.Node = _airpls()
        bl.inputs["data"].value = y
        bl.inputs["diff_order"].value = 3
        self.assertIsInstance(bl, fn.Node)
        await bl
        baseline_corrected = bl.outputs["baseline_corrected"]
        baseline = bl.outputs["baseline"]
        params = bl.outputs["params"]
        self.assertIsInstance(baseline_corrected.value, np.ndarray)
        self.assertIsInstance(baseline.value, np.ndarray)
        self.assertIsInstance(params.value, dict)

    async def test_arpls(self):
        bl: fn.Node = _arpls()
        bl.inputs["data"].value = y
        bl.inputs["diff_order"].value = 3
        self.assertIsInstance(bl, fn.Node)
        await bl
        baseline_corrected = bl.outputs["baseline_corrected"]
        baseline = bl.outputs["baseline"]
        params = bl.outputs["params"]
        self.assertIsInstance(baseline_corrected.value, np.ndarray)
        self.assertIsInstance(baseline.value, np.ndarray)
        self.assertIsInstance(params.value, dict)

    async def test_asls(self):
        bl: fn.Node = _asls()
        bl.inputs["data"].value = y
        bl.inputs["diff_order"].value = 3
        self.assertIsInstance(bl, fn.Node)
        await bl
        baseline_corrected = bl.outputs["baseline_corrected"]
        baseline = bl.outputs["baseline"]
        params = bl.outputs["params"]
        self.assertIsInstance(baseline_corrected.value, np.ndarray)
        self.assertIsInstance(baseline.value, np.ndarray)
        self.assertIsInstance(params.value, dict)

    async def test_aspls(self):
        bl: fn.Node = _aspls()
        bl.inputs["data"].value = y
        bl.inputs["diff_order"].value = 3
        self.assertIsInstance(bl, fn.Node)
        await bl
        baseline_corrected = bl.outputs["baseline_corrected"]
        baseline = bl.outputs["baseline"]
        params = bl.outputs["params"]
        self.assertIsInstance(baseline_corrected.value, np.ndarray)
        self.assertIsInstance(baseline.value, np.ndarray)
        self.assertIsInstance(params.value, dict)

    async def test_derpsalsa(self):
        bl: fn.Node = _derpsalsa()
        bl.inputs["data"].value = y
        bl.inputs["diff_order"].value = 3
        self.assertIsInstance(bl, fn.Node)
        await bl
        baseline_corrected = bl.outputs["baseline_corrected"]
        baseline = bl.outputs["baseline"]
        params = bl.outputs["params"]
        self.assertIsInstance(baseline_corrected.value, np.ndarray)
        self.assertIsInstance(baseline.value, np.ndarray)
        self.assertIsInstance(params.value, dict)

    async def test_drpls(self):
        bl: fn.Node = _drpls()
        bl.inputs["data"].value = y
        bl.inputs["diff_order"].value = 3
        self.assertIsInstance(bl, fn.Node)
        await bl
        baseline_corrected = bl.outputs["baseline_corrected"]
        baseline = bl.outputs["baseline"]
        params = bl.outputs["params"]
        self.assertIsInstance(baseline_corrected.value, np.ndarray)
        self.assertIsInstance(baseline.value, np.ndarray)
        self.assertIsInstance(params.value, dict)

    async def test_iarpls(self):
        bl: fn.Node = _iarpls()
        bl.inputs["data"].value = y
        bl.inputs["diff_order"].value = 3
        self.assertIsInstance(bl, fn.Node)
        await bl
        baseline_corrected = bl.outputs["baseline_corrected"]
        baseline = bl.outputs["baseline"]
        params = bl.outputs["params"]
        self.assertIsInstance(baseline_corrected.value, np.ndarray)
        self.assertIsInstance(baseline.value, np.ndarray)
        self.assertIsInstance(params.value, dict)

    async def test_iasls(self):
        bl: fn.Node = _iasls()
        bl.inputs["data"].value = y
        bl.inputs["diff_order"].value = 3
        self.assertIsInstance(bl, fn.Node)
        await bl
        baseline_corrected = bl.outputs["baseline_corrected"]
        baseline = bl.outputs["baseline"]
        params = bl.outputs["params"]
        self.assertIsInstance(baseline_corrected.value, np.ndarray)
        self.assertIsInstance(baseline.value, np.ndarray)
        self.assertIsInstance(params.value, dict)

    async def test_psalsa(self):
        bl: fn.Node = _psalsa()
        bl.inputs["data"].value = y
        bl.inputs["diff_order"].value = 3
        self.assertIsInstance(bl, fn.Node)
        await bl
        baseline_corrected = bl.outputs["baseline_corrected"]
        baseline = bl.outputs["baseline"]
        params = bl.outputs["params"]
        self.assertIsInstance(baseline_corrected.value, np.ndarray)
        self.assertIsInstance(baseline.value, np.ndarray)
        self.assertIsInstance(params.value, dict)

    async def test_flatfit(self):
        bl: fn.Node = flatfit()
        bl.inputs["data"].value = y
        self.assertIsInstance(bl, fn.Node)
        await bl
        baseline_corrected = bl.outputs["baseline_corrected"]
        baseline = bl.outputs["baseline"]
        params = bl.outputs["params"]
        self.assertIsInstance(baseline_corrected.value, np.ndarray)
        self.assertIsInstance(baseline.value, np.ndarray)
        self.assertIsInstance(params.value, dict)


class TestBaselineMorphological(unittest.IsolatedAsyncioTestCase):
    async def test_amormol(self):
        bl: fn.Node = _amormol()
        bl.inputs["data"].value = y
        self.assertIsInstance(bl, fn.Node)
        await bl
        baseline_corrected = bl.outputs["baseline_corrected"]
        baseline = bl.outputs["baseline"]
        params = bl.outputs["params"]
        self.assertIsInstance(baseline_corrected.value, np.ndarray)
        self.assertIsInstance(baseline.value, np.ndarray)
        self.assertIsInstance(params.value, dict)

    async def test_imor(self):
        bl: fn.Node = _imor()
        bl.inputs["data"].value = y
        self.assertIsInstance(bl, fn.Node)
        await bl
        baseline_corrected = bl.outputs["baseline_corrected"]
        baseline = bl.outputs["baseline"]
        params = bl.outputs["params"]
        self.assertIsInstance(baseline_corrected.value, np.ndarray)
        self.assertIsInstance(baseline.value, np.ndarray)
        self.assertIsInstance(params.value, dict)

    async def test_jbcd(self):
        bl: fn.Node = _jbcd()
        bl.inputs["data"].value = y
        self.assertIsInstance(bl, fn.Node)
        await bl
        baseline_corrected = bl.outputs["baseline_corrected"]
        baseline = bl.outputs["baseline"]
        params = bl.outputs["params"]
        self.assertIsInstance(baseline_corrected.value, np.ndarray)
        self.assertIsInstance(baseline.value, np.ndarray)
        self.assertIsInstance(params.value, dict)

    async def test_mor(self):
        bl: fn.Node = _mor()
        bl.inputs["data"].value = y
        self.assertIsInstance(bl, fn.Node)
        await bl
        baseline_corrected = bl.outputs["baseline_corrected"]
        baseline = bl.outputs["baseline"]
        params = bl.outputs["params"]
        self.assertIsInstance(baseline_corrected.value, np.ndarray)
        self.assertIsInstance(baseline.value, np.ndarray)
        self.assertIsInstance(params.value, dict)

    async def test_mormol(self):
        bl: fn.Node = _mormol()
        bl.inputs["data"].value = y
        self.assertIsInstance(bl, fn.Node)
        await bl
        baseline_corrected = bl.outputs["baseline_corrected"]
        baseline = bl.outputs["baseline"]
        params = bl.outputs["params"]
        self.assertIsInstance(baseline_corrected.value, np.ndarray)
        self.assertIsInstance(baseline.value, np.ndarray)
        self.assertIsInstance(params.value, dict)

    async def test_mpls(self):
        bl: fn.Node = _mpls()
        bl.inputs["data"].value = y
        self.assertIsInstance(bl, fn.Node)
        await bl
        baseline_corrected = bl.outputs["baseline_corrected"]
        baseline = bl.outputs["baseline"]
        params = bl.outputs["params"]
        self.assertIsInstance(baseline_corrected.value, np.ndarray)
        self.assertIsInstance(baseline.value, np.ndarray)
        self.assertIsInstance(params.value, dict)

    async def test_mpspline(self):
        bl: fn.Node = _mpspline()
        bl.inputs["data"].value = y
        self.assertIsInstance(bl, fn.Node)
        await bl
        baseline_corrected = bl.outputs["baseline_corrected"]
        baseline = bl.outputs["baseline"]
        params = bl.outputs["params"]
        self.assertIsInstance(baseline_corrected.value, np.ndarray)
        self.assertIsInstance(baseline.value, np.ndarray)
        self.assertIsInstance(params.value, dict)

    async def test_mwmv(self):
        bl: fn.Node = _mwmv()
        bl.inputs["data"].value = y
        self.assertIsInstance(bl, fn.Node)
        await bl
        baseline_corrected = bl.outputs["baseline_corrected"]
        baseline = bl.outputs["baseline"]
        params = bl.outputs["params"]
        self.assertIsInstance(baseline_corrected.value, np.ndarray)
        self.assertIsInstance(baseline.value, np.ndarray)
        self.assertIsInstance(params.value, dict)

    async def test_rolling_ball(self):
        bl: fn.Node = _rolling_ball()
        bl.inputs["data"].value = y
        self.assertIsInstance(bl, fn.Node)
        await bl
        baseline_corrected = bl.outputs["baseline_corrected"]
        baseline = bl.outputs["baseline"]
        params = bl.outputs["params"]
        self.assertIsInstance(baseline_corrected.value, np.ndarray)
        self.assertIsInstance(baseline.value, np.ndarray)
        self.assertIsInstance(params.value, dict)

    async def test_tophat(self):
        bl: fn.Node = _tophat()
        bl.inputs["data"].value = y
        self.assertIsInstance(bl, fn.Node)
        await bl
        baseline_corrected = bl.outputs["baseline_corrected"]
        baseline = bl.outputs["baseline"]
        params = bl.outputs["params"]
        self.assertIsInstance(baseline_corrected.value, np.ndarray)
        self.assertIsInstance(baseline.value, np.ndarray)
        self.assertIsInstance(params.value, dict)


class TestBaselineSpline(unittest.IsolatedAsyncioTestCase):
    async def test_corner_cutting(self):
        bl: fn.Node = _corner_cutting()
        bl.inputs["data"].value = y
        self.assertIsInstance(bl, fn.Node)
        await bl
        baseline_corrected = bl.outputs["baseline_corrected"]
        baseline = bl.outputs["baseline"]
        params = bl.outputs["params"]
        self.assertIsInstance(baseline_corrected.value, np.ndarray)
        self.assertIsInstance(baseline.value, np.ndarray)
        self.assertIsInstance(params.value, dict)

    async def test_irsqr(self):
        bl: fn.Node = _irsqr()
        bl.inputs["data"].value = y
        self.assertIsInstance(bl, fn.Node)
        await bl
        baseline_corrected = bl.outputs["baseline_corrected"]
        baseline = bl.outputs["baseline"]
        params = bl.outputs["params"]
        self.assertIsInstance(baseline_corrected.value, np.ndarray)
        self.assertIsInstance(baseline.value, np.ndarray)
        self.assertIsInstance(params.value, dict)

    async def test_mixture_model(self):
        bl: fn.Node = _mixture_model()
        bl.inputs["data"].value = y
        self.assertIsInstance(bl, fn.Node)
        await bl
        baseline_corrected = bl.outputs["baseline_corrected"]
        baseline = bl.outputs["baseline"]
        params = bl.outputs["params"]
        self.assertIsInstance(baseline_corrected.value, np.ndarray)
        self.assertIsInstance(baseline.value, np.ndarray)
        self.assertIsInstance(params.value, dict)

    async def test_pspline_airpls(self):
        bl: fn.Node = _pspline_airpls()
        bl.inputs["data"].value = y
        self.assertIsInstance(bl, fn.Node)
        await bl
        baseline_corrected = bl.outputs["baseline_corrected"]
        baseline = bl.outputs["baseline"]
        params = bl.outputs["params"]
        self.assertIsInstance(baseline_corrected.value, np.ndarray)
        self.assertIsInstance(baseline.value, np.ndarray)
        self.assertIsInstance(params.value, dict)

    async def test_pspline_arpls(self):
        bl: fn.Node = _pspline_arpls()
        bl.inputs["data"].value = y
        self.assertIsInstance(bl, fn.Node)
        await bl
        baseline_corrected = bl.outputs["baseline_corrected"]
        baseline = bl.outputs["baseline"]
        params = bl.outputs["params"]
        self.assertIsInstance(baseline_corrected.value, np.ndarray)
        self.assertIsInstance(baseline.value, np.ndarray)
        self.assertIsInstance(params.value, dict)

    async def test_pspline_asls(self):
        bl: fn.Node = _pspline_asls()
        bl.inputs["data"].value = y
        self.assertIsInstance(bl, fn.Node)
        await bl
        baseline_corrected = bl.outputs["baseline_corrected"]
        baseline = bl.outputs["baseline"]
        params = bl.outputs["params"]
        self.assertIsInstance(baseline_corrected.value, np.ndarray)
        self.assertIsInstance(baseline.value, np.ndarray)
        self.assertIsInstance(params.value, dict)

    async def test_pspline_aspls(self):
        bl: fn.Node = _pspline_aspls()
        bl.inputs["data"].value = y
        self.assertIsInstance(bl, fn.Node)
        await bl
        baseline_corrected = bl.outputs["baseline_corrected"]
        baseline = bl.outputs["baseline"]
        params = bl.outputs["params"]
        self.assertIsInstance(baseline_corrected.value, np.ndarray)
        self.assertIsInstance(baseline.value, np.ndarray)
        self.assertIsInstance(params.value, dict)

    async def test_pspline_derpsalsa(self):
        bl: fn.Node = _pspline_derpsalsa()
        bl.inputs["data"].value = y
        self.assertIsInstance(bl, fn.Node)
        await bl
        baseline_corrected = bl.outputs["baseline_corrected"]
        baseline = bl.outputs["baseline"]
        params = bl.outputs["params"]
        self.assertIsInstance(baseline_corrected.value, np.ndarray)
        self.assertIsInstance(baseline.value, np.ndarray)
        self.assertIsInstance(params.value, dict)

    async def test_pspline_drpls(self):
        bl: fn.Node = _pspline_drpls()
        bl.inputs["data"].value = y
        self.assertIsInstance(bl, fn.Node)
        await bl
        baseline_corrected = bl.outputs["baseline_corrected"]
        baseline = bl.outputs["baseline"]
        params = bl.outputs["params"]
        self.assertIsInstance(baseline_corrected.value, np.ndarray)
        self.assertIsInstance(baseline.value, np.ndarray)
        self.assertIsInstance(params.value, dict)

    async def test_pspline_iarpls(self):
        bl: fn.Node = _pspline_iarpls()
        bl.inputs["data"].value = y
        self.assertIsInstance(bl, fn.Node)
        await bl
        baseline_corrected = bl.outputs["baseline_corrected"]
        baseline = bl.outputs["baseline"]
        params = bl.outputs["params"]
        self.assertIsInstance(baseline_corrected.value, np.ndarray)
        self.assertIsInstance(baseline.value, np.ndarray)
        self.assertIsInstance(params.value, dict)

    async def test_pspline_iasls(self):
        bl: fn.Node = _pspline_iasls()
        bl.inputs["data"].value = y
        self.assertIsInstance(bl, fn.Node)
        await bl
        baseline_corrected = bl.outputs["baseline_corrected"]
        baseline = bl.outputs["baseline"]
        params = bl.outputs["params"]
        self.assertIsInstance(baseline_corrected.value, np.ndarray)
        self.assertIsInstance(baseline.value, np.ndarray)
        self.assertIsInstance(params.value, dict)

    async def test_pspline_mpls(self):
        bl: fn.Node = _pspline_mpls()
        bl.inputs["data"].value = y
        self.assertIsInstance(bl, fn.Node)
        await bl
        baseline_corrected = bl.outputs["baseline_corrected"]
        baseline = bl.outputs["baseline"]
        params = bl.outputs["params"]
        self.assertIsInstance(baseline_corrected.value, np.ndarray)
        self.assertIsInstance(baseline.value, np.ndarray)
        self.assertIsInstance(params.value, dict)

    async def test_pspline_psalsa(self):
        bl: fn.Node = _pspline_psalsa()
        bl.inputs["data"].value = y
        self.assertIsInstance(bl, fn.Node)
        await bl
        baseline_corrected = bl.outputs["baseline_corrected"]
        baseline = bl.outputs["baseline"]
        params = bl.outputs["params"]
        self.assertIsInstance(baseline_corrected.value, np.ndarray)
        self.assertIsInstance(baseline.value, np.ndarray)
        self.assertIsInstance(params.value, dict)


class TestBaselineSmoothing(unittest.IsolatedAsyncioTestCase):
    async def test_ipsa(self):
        bl: fn.Node = _ipsa()
        bl.inputs["data"].value = y
        self.assertIsInstance(bl, fn.Node)
        await bl
        baseline_corrected = bl.outputs["baseline_corrected"]
        baseline = bl.outputs["baseline"]
        params = bl.outputs["params"]
        self.assertIsInstance(baseline_corrected.value, np.ndarray)
        self.assertIsInstance(baseline.value, np.ndarray)
        self.assertIsInstance(params.value, dict)

    async def test_noise_median(self):
        bl: fn.Node = _noise_median()
        bl.inputs["data"].value = y
        self.assertIsInstance(bl, fn.Node)
        await bl
        baseline_corrected = bl.outputs["baseline_corrected"]
        baseline = bl.outputs["baseline"]
        params = bl.outputs["params"]
        self.assertIsInstance(baseline_corrected.value, np.ndarray)
        self.assertIsInstance(baseline.value, np.ndarray)
        self.assertIsInstance(params.value, dict)

    async def test_ria(self):
        bl: fn.Node = _ria()
        bl.inputs["data"].value = y
        self.assertIsInstance(bl, fn.Node)
        await bl
        baseline_corrected = bl.outputs["baseline_corrected"]
        baseline = bl.outputs["baseline"]
        params = bl.outputs["params"]
        self.assertIsInstance(baseline_corrected.value, np.ndarray)
        self.assertIsInstance(baseline.value, np.ndarray)
        self.assertIsInstance(params.value, dict)

    async def test_snip(self):
        bl: fn.Node = _snip()
        bl.inputs["data"].value = y
        self.assertIsInstance(bl, fn.Node)
        await bl
        baseline_corrected = bl.outputs["baseline_corrected"]
        baseline = bl.outputs["baseline"]
        params = bl.outputs["params"]
        self.assertIsInstance(baseline_corrected.value, np.ndarray)
        self.assertIsInstance(baseline.value, np.ndarray)
        self.assertIsInstance(params.value, dict)

    async def test_swima(self):
        bl: fn.Node = _swima()
        bl.inputs["data"].value = y
        self.assertIsInstance(bl, fn.Node)
        await bl
        baseline_corrected = bl.outputs["baseline_corrected"]
        baseline = bl.outputs["baseline"]
        params = bl.outputs["params"]
        self.assertIsInstance(baseline_corrected.value, np.ndarray)
        self.assertIsInstance(baseline.value, np.ndarray)
        self.assertIsInstance(params.value, dict)


class TestBaselineClassification(unittest.IsolatedAsyncioTestCase):
    async def test_cwt_br(self):
        bl: fn.Node = _cwt_br()
        bl.inputs["data"].value = y
        self.assertIsInstance(bl, fn.Node)
        await bl
        baseline_corrected = bl.outputs["baseline_corrected"]
        baseline = bl.outputs["baseline"]
        params = bl.outputs["params"]
        self.assertIsInstance(baseline_corrected.value, np.ndarray)
        self.assertIsInstance(baseline.value, np.ndarray)
        self.assertIsInstance(params.value, dict)

    async def test_dietrich(self):
        bl: fn.Node = _dietrich()
        bl.inputs["data"].value = y
        self.assertIsInstance(bl, fn.Node)
        await bl
        baseline_corrected = bl.outputs["baseline_corrected"]
        baseline = bl.outputs["baseline"]
        params = bl.outputs["params"]
        self.assertIsInstance(baseline_corrected.value, np.ndarray)
        self.assertIsInstance(baseline.value, np.ndarray)
        self.assertIsInstance(params.value, dict)

    async def test_fabc(self):
        bl: fn.Node = _fabc()
        bl.inputs["data"].value = y
        self.assertIsInstance(bl, fn.Node)
        await bl
        baseline_corrected = bl.outputs["baseline_corrected"]
        baseline = bl.outputs["baseline"]
        params = bl.outputs["params"]
        self.assertIsInstance(baseline_corrected.value, np.ndarray)
        self.assertIsInstance(baseline.value, np.ndarray)
        self.assertIsInstance(params.value, dict)

    async def test_fastchrom(self):
        bl: fn.Node = _fastchrom()
        bl.inputs["data"].value = y
        self.assertIsInstance(bl, fn.Node)
        await bl
        baseline_corrected = bl.outputs["baseline_corrected"]
        baseline = bl.outputs["baseline"]
        params = bl.outputs["params"]
        self.assertIsInstance(baseline_corrected.value, np.ndarray)
        self.assertIsInstance(baseline.value, np.ndarray)
        self.assertIsInstance(params.value, dict)

    async def test_golotvin(self):
        bl: fn.Node = _golotvin()
        bl.inputs["data"].value = y
        self.assertIsInstance(bl, fn.Node)
        await bl
        baseline_corrected = bl.outputs["baseline_corrected"]
        baseline = bl.outputs["baseline"]
        params = bl.outputs["params"]
        self.assertIsInstance(baseline_corrected.value, np.ndarray)
        self.assertIsInstance(baseline.value, np.ndarray)
        self.assertIsInstance(params.value, dict)

    async def test_rubberband(self):
        bl: fn.Node = _rubberband()
        bl.inputs["data"].value = y
        self.assertIsInstance(bl, fn.Node)
        await bl
        baseline_corrected = bl.outputs["baseline_corrected"]
        baseline = bl.outputs["baseline"]
        params = bl.outputs["params"]
        self.assertIsInstance(baseline_corrected.value, np.ndarray)
        self.assertIsInstance(baseline.value, np.ndarray)
        self.assertIsInstance(params.value, dict)

    async def test_std_distribution(self):
        bl: fn.Node = _std_distribution()
        bl.inputs["data"].value = y
        self.assertIsInstance(bl, fn.Node)
        await bl
        baseline_corrected = bl.outputs["baseline_corrected"]
        baseline = bl.outputs["baseline"]
        params = bl.outputs["params"]
        self.assertIsInstance(baseline_corrected.value, np.ndarray)
        self.assertIsInstance(baseline.value, np.ndarray)
        self.assertIsInstance(params.value, dict)


class TestBaselineOptimizers(unittest.IsolatedAsyncioTestCase):
    async def test_adaptive_minmax(self):
        bl: fn.Node = _adaptive_minmax()
        bl.inputs["data"].value = y
        self.assertIsInstance(bl, fn.Node)
        await bl
        baseline_corrected = bl.outputs["baseline_corrected"]
        baseline = bl.outputs["baseline"]
        params = bl.outputs["params"]
        self.assertIsInstance(baseline_corrected.value, np.ndarray)
        self.assertIsInstance(baseline.value, np.ndarray)
        self.assertIsInstance(params.value, dict)

    async def test_collab_pls(self):
        bl: fn.Node = _collab_pls()
        bl.inputs["data"].value = np.tile(y, (4, 1))
        self.assertIsInstance(bl, fn.Node)
        await bl
        baseline_corrected = bl.outputs["baseline_corrected"]
        baseline = bl.outputs["baseline"]
        params = bl.outputs["params"]
        self.assertIsInstance(baseline_corrected.value, np.ndarray)
        self.assertIsInstance(baseline.value, np.ndarray)
        self.assertIsInstance(params.value, dict)

    async def test_custom_bc(self):
        bl: fn.Node = _custom_bc()
        bl.inputs["data"].value = y
        self.assertIsInstance(bl, fn.Node)
        await bl
        baseline_corrected = bl.outputs["baseline_corrected"]
        baseline = bl.outputs["baseline"]
        params = bl.outputs["params"]
        self.assertIsInstance(baseline_corrected.value, np.ndarray)
        self.assertIsInstance(baseline.value, np.ndarray)
        self.assertIsInstance(params.value, dict)

    async def test_optimize_extended_range(self):
        bl: fn.Node = _optimize_extended_range()
        bl.inputs["data"].value = y
        self.assertIsInstance(bl, fn.Node)
        await bl
        baseline_corrected = bl.outputs["baseline_corrected"]
        baseline = bl.outputs["baseline"]
        params = bl.outputs["params"]
        self.assertIsInstance(baseline_corrected.value, np.ndarray)
        self.assertIsInstance(baseline.value, np.ndarray)
        self.assertIsInstance(params.value, dict)


class TestbaselineNodes(unittest.IsolatedAsyncioTestCase):
    async def test_estimate_baseline_regions_node(self):
        bl: fn.Node = estimate_baseline_regions_node()
        bl.inputs["y"].value = y
        bl.inputs["x"].value = x
        self.assertIsInstance(bl, fn.Node)
        await bl
        baseline = bl.outputs["baseline"].value
        is_baseline = bl.outputs["is_baseline"].value
        self.assertIsInstance(baseline, np.ndarray)
        self.assertEqual(baseline.shape, y.shape)
        self.assertIsInstance(is_baseline, np.ndarray)
        self.assertEqual(is_baseline.shape, y.shape)
        self.assertEqual(is_baseline.dtype, bool)
        self.assertGreaterEqual(is_baseline.sum(), 200)
        self.assertLessEqual(is_baseline.sum(), 300)
