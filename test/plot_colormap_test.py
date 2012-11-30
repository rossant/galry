import unittest
from galry import *
import numpy as np
from test import GalryTest

class PM(PaintManager):
    def initialize(self):
        x = np.array([-.5, .5, .5, .5, .5, -.5, -.5, -.5]).reshape((4, 2))
        y = np.array([-.5, -.5, -.5, .5, .5, .5, .5, -.5]).reshape((4, 2))
        color = np.zeros((4, 3))
        color[0,:] = (1, 0, 0)
        color[1,:] = (0, 1, 0)
        color[2,:] = (0, 0, 1)
        color[3,:] = (1, 1, 1)
        index = [3, 3, 3, 3, 3, 3, 3, 3]
        self.add_visual(PlotVisual, x=x, y=y, color=color,
            color_array_index=index,
            primitive_type='LINES')

class PlotColormapTest(GalryTest):
    def test(self):
        self.show(paint_manager=PM)

if __name__ == '__main__':
    unittest.main()
    # show_basic_window(paint_manager=PM)
