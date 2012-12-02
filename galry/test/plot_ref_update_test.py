import unittest
import numpy as np
from galry import *
from test import GalryTest

class PM(PaintManager):
    def initialize(self):
        position = np.zeros((4, 2))
        position[:,0] = [-.5, .5, .5, -.5]
        position[:,1] = [-.5, -.5, .5, .5]

        # we first add a plot with square coordinates but black
        self.add_visual(PlotVisual, position=np.random.randn(4, 2)*.2, color=(1.,) * 4)
        # add a new visual where the position variable refers to the position
        # variable of the first visual. The same memory buffer is shared
        # for both visuals on system memory and graphics memory.
        self.add_visual(PlotVisual, position=RefVar('visual0', 'position'), 
            color=(1.,) * 4)
        self.set_data(position=position, visual='visual0', primitive_type='LINE_LOOP')
        
class PlotRefUpdateTest(GalryTest):
    def test(self):
        self.show(paint_manager=PM)

if __name__ == '__main__':
    unittest.main()
