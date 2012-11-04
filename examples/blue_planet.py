import os
from galry import *
import pylab as plt

class EarthPaintManager(PaintManager):
    def initialize(self):
        # get the absolute path of the file
        path = os.path.dirname(os.path.realpath(__file__))
        # load the texture from an image thanks to matplotlib
        texture = plt.imread(os.path.join(path, "images/earth.png"))
        # add a textured rectangle
        self.create_dataset(TextureTemplate, texture=texture)       

if __name__ == '__main__':
    # create window
    window = show_basic_window(paint_manager=EarthPaintManager,
                               constrain_ratio=True,
                               constrain_navigation=False,)
