import funcnodes as fn
import unittest
import numpy as np
from funcnodes_span.normalization import _norm, NormMode, density_normalization_node
from scipy.datasets import electrocardiogram


# x = electrocardiogram()[2000:4000]
class TestNormalization(unittest.IsolatedAsyncioTestCase):
    async def test_default(self):
        norm: fn.Node = _norm()
        norm.inputs["array"].value = electrocardiogram()[2000:4000]
        self.assertIsInstance(norm, fn.Node)
        await norm
        out = norm.outputs["out"]
        self.assertIsInstance(out.value, np.ndarray)

    async def test_non_default_mode(self):
        norm: fn.Node = _norm()
        norm.inputs["array"].value = electrocardiogram()[2000:4000]
        norm.inputs["mode"].value = NormMode.SUM_ABS
        self.assertIsInstance(norm, fn.Node)
        await norm
        out = norm.outputs["out"]
        self.assertIsInstance(out.value, np.ndarray)

    async def test_desity_norm(self):
        norm: fn.Node = density_normalization_node()
        norm.inputs["x"].value = np.log10(np.arange(1, 100))
        norm.inputs["y"].value = 2 * norm.inputs["x"].value
        self.assertIsInstance(norm, fn.Node)
        await norm
        x_new = norm.outputs["x_new"].value
        self.assertIsInstance(x_new, np.ndarray)
        self.assertEqual(len(x_new), 229)
        np.testing.assert_equal(x_new * 2, norm.outputs["y_new"].value)
        np.testing.assert_almost_equal(np.diff(x_new), x_new[1] - x_new[0])
