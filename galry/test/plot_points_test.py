import unittest
from galry import *
from test import GalryTest
import numpy as np

class PM(PaintManager):
    def initialize(self):
        n = 100000
        x0 = np.linspace(-.5, .5, n)
        x1 = .5 * np.ones(n)
        x = np.hstack((x0, x1, x0, -x1))
        
        y0 = -.5 * np.ones(n)
        y1 = np.linspace(-.5, .5, n)
        y = np.hstack((y0, y1, -y0, y1))
        
        self.add_visual(PlotVisual, x=x, y=y, color=(1., 1., 1., 1.),
            primitive_type='POINTS')

class PlotPointsTest(GalryTest):
    def test(self):
        self.show(paint_manager=PM)

if __name__ == '__main__':
    unittest.main()
