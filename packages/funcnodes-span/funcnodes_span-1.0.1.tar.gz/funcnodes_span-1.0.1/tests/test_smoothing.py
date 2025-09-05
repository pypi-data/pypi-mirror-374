import funcnodes as fn
import unittest
import numpy as np
from funcnodes_span.smoothing import _smooth, SmoothMode
from scipy.datasets import electrocardiogram


# x = electrocardiogram()[2000:4000]
class TestSmoothing(unittest.IsolatedAsyncioTestCase):
    async def test_default(self):
        smooth: fn.Node = _smooth()
        smooth.inputs["y"].value = electrocardiogram()[2000:4000]
        self.assertIsInstance(smooth, fn.Node)
        await smooth
        out = smooth.outputs["smoothed"]
        self.assertIsInstance(out.value, np.ndarray)

    async def test_non_default_mode(self):
        norm: fn.Node = _smooth()
        norm.inputs["y"].value = electrocardiogram()[2000:4000]
        norm.inputs["mode"].value = SmoothMode.MOVING_AVERAGE
        self.assertIsInstance(norm, fn.Node)
        await norm
        out = norm.outputs["smoothed"]
        self.assertIsInstance(out.value, np.ndarray)
