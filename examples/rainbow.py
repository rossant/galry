from galry import *
import numpy as np
from matplotlib.colors import hsv_to_rgb

def colormap(x):
    """Colorize a 2D grayscale array.
    
    Arguments: 
      * x:an NxM array with values in [0,1] 
    
    Returns:
      * y: an NxMx3 array with a rainbow color palette.
    
    """
    x = np.clip(x, 0., 1.)
    
    # initial and final gradient colors, here rainbow gradient
    col0 = np.array([.67, .91, .65]).reshape((1, 1, -1))
    col1 = np.array([0., 1., 1.]).reshape((1, 1, -1))
    
    col0 = np.tile(col0, x.shape + (1,))
    col1 = np.tile(col1, x.shape + (1,))
    
    x = np.tile(x.reshape(x.shape + (1,)), (1, 1, 3))
    
    return hsv_to_rgb(col0 + (col1 - col0) * x)
    
class CorrelationMatrixPaintManager(PaintManager):
    def initialize(self):
        n = 256
        # create linear values as 2D texture
        data = np.linspace(0., 1., n * n).reshape((n, n))
        # colorize the texture
        texture = colormap(data)
        # show the texture
        self.create_dataset(TextureTemplate, shape=(n, n),
            ncomponents=texture.shape[2],
            )
        self.set_data(tex_sampler=texture)
    
if __name__ == '__main__':
    show_basic_window(paint_manager=CorrelationMatrixPaintManager)
    