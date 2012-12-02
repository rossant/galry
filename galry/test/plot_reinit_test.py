import unittest
from galry import *
from test import GalryTest
import numpy as np

class PM(PaintManager):
    def initialize(self):
        position = np.random.randn(1000, 2) * .2
        self.add_visual(PlotVisual, position=position, primitive_type='POINTS',
            color=(1., 1., 1., 1.))
        # initialize the visual again, but takes only the data defined in
        # visual.initialize()
        self.reinitialize_visual(x=[-.5, .5, .5, -.5, -.5],
                                 y=[-.5, -.5, .5, .5, -.5],
                                 primitive_type='LINE_STRIP',
                                 color=(1.,) * 4)

class PlotReinitTest(GalryTest):
    def test(self):
        self.show(paint_manager=PM)

if __name__ == '__main__':
    unittest.main()
    # show_basic_window(paint_manager=PM)
    