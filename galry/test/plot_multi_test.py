import unittest
from galry import *
from test import GalryTest
import numpy as np

class PM(PaintManager):
    def initialize(self):
        x = np.empty((4, 2))
        x[0,:] = (.5, -.5)
        x[1,:] = (.5, .5)
        x[2,:] = (.5, -.5)
        x[3,:] = (-.5, -.5)
        
        y = np.empty((4, 2))
        y[0,:] = (-.5, -.5)
        y[1,:] = (.5, -.5)
        y[2,:] = (.5, .5)
        y[3,:] = (-.5, .5)
        
        color = np.ones((5, 4))
        color[-1, :] = 0
        
        self.add_visual(PlotVisual, x=x, y=y, color=color)

class PlotMultiTest(GalryTest):
    def test(self):
        self.show(paint_manager=PM)

if __name__ == '__main__':
    unittest.main()
