import unittest
import numpy as np
from galry import *
from test import GalryTest

class PM(PaintManager):
    def initialize(self):
        x = [-.5, .5, .5]
        y = [-.5, -.5, .5]
        self.add_visual(PlotVisual, x=x, y=y, color=(1., 1., 1., 1.))
        x2 = [.5, -.5, -.5]
        y2 = [.5, .5, -.5]
        self.add_visual(PlotVisual, x=x2, y=y2, color=(1., 1., 1., 1.),
                        name='visual2')#, visible=True)

class PlotDoubleTest(GalryTest):
    def start(self):
        self.show(paint_manager=PM)

if __name__ == '__main__':
    # unittest.main()
    show_basic_window(paint_manager=PM)