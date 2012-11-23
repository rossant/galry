import unittest
from galry import *
from test import GalryTest

class PM(PaintManager):
    def initialize(self):
        self.add_visual(PlotVisual, x=[-.5, .5, .5, -.5, -.5],
                y=[-.5, -.5, .5, .5, -.5], color=(1., 1., 1., 1.))

class PlotDefaultTest(GalryTest):
    def test(self):
        self.show(paint_manager=PM)

if __name__ == '__main__':
    unittest.main()

