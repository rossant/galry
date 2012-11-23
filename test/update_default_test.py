import unittest
from galry import *
from test import GalryTest
import numpy as np

class PM(PaintManager):
    def initialize(self):
        # random data
        position = np.random.randn(10, 2) * .2
        self.add_visual(PlotVisual, position=position, color=(1., 1., 1., 1.))
        # then we update to have a square
        x = np.array([-.5, .5, .5, -.5, -.5])
        y = np.array([-.5, -.5, .5, .5, -.5])
        position = np.hstack((x.reshape((-1, 1)), y.reshape((-1, 1))))
        self.set_data(position=position)
        
class UpdateDefaultTest(GalryTest):
    def test(self):
        window = self.show(paint_manager=PM)

if __name__ == '__main__':
    unittest.main()
    # show_basic_window(paint_manager=PM)