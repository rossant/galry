import unittest
from galry import *
from test import GalryTest

class PM(PaintManager):
    def initialize(self):
        # we first add a plot with square coordinates but black
        self.add_visual(PlotVisual, x=[-.5, .5, .5, -.5, -.5],
                y=[-.5, -.5, .5, .5, -.5], color=(0.,) * 4)
        # add a new visual where the position variable refers to the position
        # variable of the first visual. The same memory buffer is shared
        # for both visuals on system memory and graphics memory.
        self.add_visual(PlotVisual, position=RefVar('visual0', 'position'), 
            color=(1.,) * 4)
        
class PlotRefTest(GalryTest):
    def test(self):
        self.show(paint_manager=PM)

if __name__ == '__main__':
    unittest.main()
