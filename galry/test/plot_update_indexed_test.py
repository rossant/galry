import unittest
from galry import *
from test import GalryTest

class PM(PaintManager):
    def initialize(self):
        position = np.zeros((4, 2))
        position[:,0] = [-.5, .5, .5, -.5]
        position[:,1] = [-.5, -.5, .5, .5]
        
        # update the index to a bigger array
        index0 = [0, 2, 1]
        index1 = [0, 1, 2, 3, 0]
        
        self.add_visual(PlotVisual, position=position, color=(1., 1., 1., 1.),
            primitive_type='LINE_STRIP', index=index0)
        self.set_data(index=index1)
            
class PlotUpdateIndexedTest(GalryTest):
    def test(self):
        self.show(paint_manager=PM)

if __name__ == '__main__':
    unittest.main()
    # show_basic_window(paint_manager=PM)
