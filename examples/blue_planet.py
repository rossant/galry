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
        
class EarthPlot(GalryWidget):
    def initialize(self):
        # set custom paint manager
        self.set_companion_classes(paint_manager=EarthPaintManager)
        # initialize companion classes
        self.initialize_companion_classes()
        # not constrain navigation to [-1,1]^2
        self.interaction_manager.constrain_navigation = False
        # keep a square viewport ratio when resizing the window
        self.constrain_ratio = True        

if __name__ == '__main__':
    # create window
    window = show_basic_window(EarthPlot)
