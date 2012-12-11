import unittest
from galry import *
from test import GalryTest
import numpy as np

class PM(PaintManager):
    def initialize(self):
        d = 4e-3
        coordinates = np.array([[-.5, -.5, .5, .5],
                                [-.5 + d, -.5 + d, .5 - d, .5 - d]])
        color = np.array([[1., 1., 1., 1.],
                          [0., 0., 0., 1.]])
        self.add_visual(RectanglesVisual, coordinates=coordinates,
            color=color)

class RectanglesDefaultTest(GalryTest):
    def test(self):
        self.show(paint_manager=PM)

if __name__ == '__main__':
    # unittest.main()    
    show_basic_window(paint_manager=PM)
