from galry import *
import numpy as np
from pylab import imread

class PM(PaintManager):
    def initialize(self):
        texture = np.zeros((1, 10, 4))
        texture[0,0,:] = 1
        # TODO
        self.add_visual(TextureVisual, texture=texture)
    
if __name__ == '__main__':
    show_basic_window(paint_manager=PM)
    