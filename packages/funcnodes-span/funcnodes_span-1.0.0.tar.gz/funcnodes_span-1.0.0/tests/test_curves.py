import unittest
import numpy as np
from funcnodes_span.curves import knee_point_detection_node, estimate_noise_node
import funcnodes as fn

fn.config.IN_NODE_TEST = True


class TestCurveFunctions(unittest.IsolatedAsyncioTestCase):
    async def test_knee_point_detection(self):
        x = np.linspace(1, 10, 1000)
        y = 1 / x
        node = knee_point_detection_node()
        node.inputs["x"].value = x
        node.inputs["y"].value = y
        await node
        knee_idx = node.outputs["knee_idx"].value
        knee_x = node.outputs["knee_x"].value
        knee_y = node.outputs["knee_y"].value

        self.assertEqual(knee_idx, 240)
        self.assertEqual(knee_x, x[knee_idx])
        self.assertEqual(knee_y, y[knee_idx])

    async def test_estimate_noise(self):
        x = np.linspace(0, 30, 10000)
        # gaussian distribution
        y = np.exp(-((x - 15) ** 2)) + np.random.RandomState(42).normal(0, 0.1, len(x))

        node = estimate_noise_node()
        node.inputs["x"].value = x
        node.inputs["y"].value = y
        await node
        noise_level = node.outputs["noise_level"].value

        self.assertAlmostEqual(noise_level, 0.3, delta=0.05)
