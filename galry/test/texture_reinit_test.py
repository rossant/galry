import unittest
from galry import *
from test import GalryTest
import numpy as np

class PM(PaintManager):
    def initialize(self):
        self.add_visual(TextureVisual, texture=np.zeros((2, 2, 3)))
        # initialize the visual again, but takes only the data defined in
        # visual.initialize()
        tex = np.zeros((600, 600, 3))
        a = 150
        tex[a:-a,a:-a,:] = 1
        tex[a+1:-a-1,a+1:-a-1,:] = 0
        self.reinitialize_visual(texture=tex)

class PlotReinitTest(GalryTest):
    def test(self):
        self.show(paint_manager=PM)

if __name__ == '__main__':
    unittest.main()
    # show_basic_window(paint_manager=PM)
    