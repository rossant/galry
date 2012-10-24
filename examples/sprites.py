from galry import *
import os
import numpy as np

class SpritesPaintManager(PaintManager):
    def initialize(self):
        import pylab as plt
        # get the absolute path of the file
        path = os.path.dirname(os.path.realpath(__file__))
        # load the texture from an image thanks to matplotlib
        texture = plt.imread(os.path.join(path, "images/earth.png"))
        x, y = np.meshgrid(np.linspace(-1.,1.,10), np.linspace(-1.,1.,10))
        self.add_sprites(x.ravel(), y.ravel(), color=(1,1,1),
                         texture=texture, size=64)

if __name__ == '__main__':
    window = show_basic_window(paint_manager=SpritesPaintManager)
    