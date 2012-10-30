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
        n = 100
        x, y = np.meshgrid(np.linspace(-1.,1.,n), np.linspace(-1.,1.,n))
        self.create_dataset(SpriteTemplate, size=len(x), shape=(64.,64.))
        self.set_data(position=positions, tex_sampler=texture)

if __name__ == '__main__':
    window = show_basic_window(paint_manager=SpritesPaintManager)
    