import unittest
from galry import *
from test import GalryTest
import numpy as np

import galry.glrenderer
galry.glrenderer.MAX_VBO_SIZE = 1000


class PM(PaintManager):
    def initialize(self):
        n = 20000#16325
        v = np.linspace(-.5, .5, n)
        w = .5 * np.ones(n)
        x = np.vstack((v, -v, w, -w))
        y = np.vstack((-w, w, v, -v))
        
        x = np.vstack((x,) * 4)
        y = np.vstack((y,) * 4)
        
        color = np.ones((x.shape[0], 4))
        
        self.add_visual(PlotVisual, x=x, y=y, color=color,
            primitive_type='LINE_STRIP')

class PlotSliceTest(GalryTest):
    def test(self):
        self.show(paint_manager=PM)

if __name__ == '__main__':
    unittest.main()
    # show_basic_window(paint_manager=PM)
