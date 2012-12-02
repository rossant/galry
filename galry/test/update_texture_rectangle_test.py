import unittest
import numpy as np
from pylab import imread
from galry import *
from test import GalryTest, get_image_path

class PM(PaintManager):
    def initialize(self):
        texture0 = np.zeros((2, 10, 4))
        texture1 = imread(get_image_path('_REF.png'))
        texture1 = texture1[:,75:-75,:]
        
        self.add_visual(TextureVisual, texture=texture0,
            points=(-.75, -1., .75, 1.))
        self.set_data(texture=texture1)
        
class UpdateTextureRectangleTest(GalryTest):
    def test(self):
        window = self.show(paint_manager=PM)

if __name__ == '__main__':
    unittest.main()
    # show_basic_window(paint_manager=PM)
    
