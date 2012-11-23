import unittest
from galry import *
from test import GalryTest

class PM(PaintManager):
    def initialize(self):
        x = [-.5, .5, .5, .5, .5, -.5, -.5, -.5]
        y = [-.5, -.5, -.5, .5, .5, .5, .5, -.5]
        self.add_visual(PlotVisual, x=x, y=y, color=(1., 1., 1., 1.),
            primitive_type='LINES')

class PlotLinesTest(GalryTest):
    def test(self):
        self.show(paint_manager=PM)

if __name__ == '__main__':
    unittest.main()
