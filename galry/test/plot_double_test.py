import unittest
import numpy as np
from galry import *
from test import GalryTest

class PM(PaintManager):
    def initialize(self):
        color = (1.,) * 4
        x = [-.5, .5, .5]
        y = [-.5, -.5, .5]
        self.add_visual(PlotVisual, x=x, y=y, color=color)
        x2 = [.5, -.5, -.5]
        y2 = [.5, .5, -.5]
        self.add_visual(PlotVisual, x=x2, y=y2, color=color)

class PlotDoubleTest(GalryTest):
    def test(self):
        self.show(paint_manager=PM)

if __name__ == '__main__':
    unittest.main()
    