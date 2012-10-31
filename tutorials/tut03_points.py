"""Tutorial 03: Displaying points.

This tutorial shows how to render some data as points, and presents the
navigation system.

"""

# We import galry.
from galry import *

# We also import numpy.random in order to generate random data.
import numpy.random as rdn

class MyPaintManager(PaintManager):
    def initialize(self):
        # We define some data here.
        # Try to increase the number of points to see what your GPU is capable
        # of (be brave, try the million!).
        # The initial coordinate range of the window is [-1, 1]^2.
        # X, Y = 0.2 * rdn.randn(2, 10000)
        data = 0.2 * rdn.randn(10000, 2)
        
        # We plot data with coordinates X and Y, rendered by default
        # as yellow points.
        # self.add_plot(X, Y)
        ds = self.create_dataset(PlotTemplate, size=len(data))
        self.set_data(position=data)
        
        self.parent.display_fps = True

# By default, you can navigate into the window with the following commands:
#   * wheel scroll to zoom in/out,
#   * mouse move while pressing the left button to pan,
#   * mouse move while pressing the middle button to drag a zoom box,
#   * mouse move while pressing the right button to zoom in/out,
#   * double click or press R to reinitialize the view.
show_basic_window(paint_manager=MyPaintManager)
