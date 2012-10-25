"""Benchmark 01: Displaying points.

"""

from galry import *
import numpy.random as rdn

# Number of points.
N = 1000000

class MyPaintManager(PaintManager):
    def initialize(self):
        self.parent.display_fps = True
        self.interaction_manager.constrain_navigation = False
        X, Y = 0.2 * rdn.randn(2, N)
        self.add_plot(X, Y)
show_basic_window(paint_manager=MyPaintManager)
