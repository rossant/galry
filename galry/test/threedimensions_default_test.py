import unittest
from galry import *
from test import GalryTest
import numpy as np

class PM(PaintManager):
    def initialize(self):
        position = np.array([[-.5, -.5, 0],
                             [.5, -.5, 0],
                             [-.5, .5, 0],
                             [.5, .5, 0]])
                             
        normal = np.zeros((4, 3))
        normal[:, 2] = -1
        color = np.ones((10, 4))
        
        self.add_visual(MeshVisual, position=position,
            normal=normal, color=color, primitive_type='TRIANGLE_STRIP')

class ThreeDimensionsDefaultTest(GalryTest):
    def test(self):
        self.show(paint_manager=PM)

if __name__ == '__main__':
    unittest.main()
    # show_basic_window(paint_manager=PM)