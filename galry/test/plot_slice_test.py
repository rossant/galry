import unittest
from galry import *
from test import GalryTest
import numpy as np

class PM(PaintManager):
    def initialize(self):
        n = 100000
        v = .5 * np.ones(n)
        x = np.hstack((-v, v, v, -v, -v))
        y = np.hstack((-v, -v, v, v, -v))
        
        self.add_visual(PlotVisual, x=x, y=y, color=(1., 1., 1., 1.),
            primitive_type='LINE_STRIP')

class PlotSliceTest(GalryTest):
    def test(self):
        self.show(paint_manager=PM)

if __name__ == '__main__':
    unittest.main()
