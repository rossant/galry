"""Benchmark 01: Displaying points.

"""

from galry import *
import numpy.random as rdn

# Number of points.
N = 1e6

class MyPaintManager(PaintManager):
    def initialize(self):
        self.create_dataset(PlotTemplate, position=0.2 * rdn.randn(N, 2),
            primitive_type=PrimitiveType.Points)
        
show_basic_window(paint_manager=MyPaintManager, display_fps=True,
    constrain_navigation=False)
