import funcnodes as fn
from ._curves import knee_point_detection, estimate_noise

knee_point_detection_node = fn.NodeDecorator(
    id="span.curves.knee_point_detection",
    name="Knee point detection",
    outputs=[{"name": "knee_idx"}, {"name": "knee_x"}, {"name": "knee_y"}],
)(knee_point_detection)

estimate_noise_node = fn.NodeDecorator(
    id="span.curves.estimate_noise",
    name="Estimate noise",
    outputs=[{"name": "noise_level"}],
)(estimate_noise)

CURVES_NODE_SHELF = fn.Shelf(
    nodes=[knee_point_detection_node, estimate_noise_node],
    subshelves=[],
    name="Curves",
    description="Analysis of curves and spectra",
)
