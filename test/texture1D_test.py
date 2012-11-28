import unittest
from galry import *
from test import GalryTest
import numpy as np

class PM(PaintManager):
    def initialize(self):
        texture = np.ones((1, 10, 3))
        self.add_visual(TextureVisual, texture=texture,
            points=(-.5,-.5-1./600,.5,-.5+1./600))
        self.add_visual(TextureVisual, texture=texture,
            points=(-.5,.5-1./600,.5,.5+1./600))
        self.add_visual(TextureVisual, texture=texture,
            points=(-.5-1./600,-.5,-.5+1./600, .5))
        self.add_visual(TextureVisual, texture=texture,
            points=(.5-1./600,-.5,.5+1./600, .5))

class TextureDefaultTest(GalryTest):
    def test(self):
        self.show(paint_manager=PM)

if __name__ == '__main__':
    unittest.main()    
    # show_basic_window(paint_manager=PM)