"""Benchmark 01: Displaying points.

"""

from galry import *
import numpy.random as rdn

# Number of points.
N = 100000000

class MyPaintManager(PaintManager):
    def initialize(self):
        self.parent.display_fps = True
        self.interaction_manager.constrain_navigation = False
        
        data = 0.2 * rdn.randn(N, 2)
        
        color = rdn.rand(N, 4)
        
        self.create_dataset(PlotTemplate, size=len(data), single_color=False)
        self.set_data(position=data, color=color)
        
        
show_basic_window(paint_manager=MyPaintManager)
