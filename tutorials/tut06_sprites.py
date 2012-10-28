"""Tutorial 06: Displaying sprites.

This tutorial shows how to display sprites, e.g. a same texture at different
positions.

"""

# We import galry.
from galry import *

# We also importnumpy.random in order to generate random data.
import numpy as np
import numpy.random as rdn

def create_texture():
    """This function creates a cross-like texture."""
    
    # We use an alpha channel for transparency of the cross outside the cross
    # itself.
    texture = np.zeros((15, 15, 4))
    texture[7, :, :] = texture[:, 7, :] = 1
    return texture

class MyPaintManager(PaintManager):
    def initialize(self):
        
        # We create a small cross texture.
        texture = create_texture()
        
        # Number of sprites.
        n = 2000
        
        # Positions of the sprites.
        position = .2 * rdn.randn(n, 2)
        
        # Color of all sprites (with transparency).
        color = rdn.rand(n, 4)
        
        # We add sprites.
        self.create_dataset(SpriteTemplate, size=n, texsize=texture.shape[0])
        self.set_data(position=position, color=color, tex_sampler=texture)

show_basic_window(paint_manager=MyPaintManager)
