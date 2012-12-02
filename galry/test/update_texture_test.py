import unittest
import numpy as np
from pylab import imread
from galry import *
from test import GalryTest, get_image_path

class PM(PaintManager):
    def initialize(self):
        texture0 = np.zeros((100, 100, 4))
        texture1 = imread(get_image_path('_REF.png'))
        
        self.add_visual(TextureVisual, texture=texture0)
        self.set_data(texture=texture1)
        
class UpdateTextureTest(GalryTest):
    def test(self):
        window = self.show(paint_manager=PM)

if __name__ == '__main__':
    unittest.main()
    # show_basic_window(paint_manager=PM)
    
