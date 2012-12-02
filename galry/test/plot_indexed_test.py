import unittest
from galry import *
from test import GalryTest

class PM(PaintManager):
    def initialize(self):
        position = np.zeros((4, 2))
        position[:,0] = [-.5, .5, .5, -.5]
        position[:,1] = [-.5, -.5, .5, .5]
        self.add_visual(PlotVisual, position=position, color=(1., 1., 1., 1.),
            primitive_type='LINES', index=[0, 1, 0, 3, 1, 2, 3, 2])

class PlotIndexedTest(GalryTest):
    def test(self):
        self.show(paint_manager=PM)

if __name__ == '__main__':
    unittest.main()

