"""Tutorial 05: Displaying a texture.

This tutorial shows how to display a colored 2D texture, and how to constrain
the window ratio.

"""

# We import galry.
from galry import *

# We also import numpy.random in order to generate random data.
import numpy.random as rdn

class MyPaintManager(PaintManager):
    def initialize(self):
        
        # We create an m x n texture as an m x n x 3 array.
        # We could also use matplotlib.pyplot.imread("image.png") to
        # load a PNG image as a RGB texture.
        self.add_textured_rectangle(rdn.rand(100, 100, 3))
        
        # GalryWidget has a special attribute to constrain the viewport ratio 
        # when navigating or resizing the window. It can be useful when
        # displaying an image, for instance.
        self.parent.constrain_ratio = True

show_basic_window(paint_manager=MyPaintManager)
