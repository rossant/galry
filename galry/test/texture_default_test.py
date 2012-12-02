import unittest
from galry import *
from test import GalryTest
import numpy as np

class PM(PaintManager):
    def initialize(self):
        texture = np.zeros((600, 600, 4))
        texture[150, 150:-150, :] = 1
        texture[-150, 150:-150, :] = 1
        texture[150:-150, 150, :] = 1
        texture[150:-150, -150, :] = 1
        self.add_visual(TextureVisual, texture=texture)

class TextureDefaultTest(GalryTest):
    def test(self):
        self.show(paint_manager=PM)

if __name__ == '__main__':
    unittest.main()    
