"""Tutorial 04: Displaying lines.

This tutorial shows how to efficiently render some data as independent lines
with different colors.

"""

# We import galry.
from galry import *

# We also import numpy and numpy.random in order to generate random data.
import numpy as np
import numpy.random as rdn

def create_data(m, n):
    """This function creates data to be displayed as m lines of size n."""
    
    # Since the window range is [-1, 1]^2, X varies from -1 to 1 here.
    # X and Y are m x n matrices, each line corresponds to one line.
    X = np.tile(np.linspace(-1., 1, n), (m, 1))
    
    # Y contains random values.
    Y = .2 / m * rdn.randn(m, n)
    
    # We shift the Y coordinates in each line.
    Y += .9 * np.linspace(-1., 1., m).reshape((-1, 1))
    
    data = np.hstack((X.reshape((-1, 1)), Y.reshape(-1, 1)))
    
    # `colors` is an m x 3 matrix, where each line contains the RGB components
    # of the corresponding line. We also could use an alpha channel
    # (transparency) with an m x 4 matrix.
    colors = rdn.rand(m, 3)
    return data, colors

class MyPaintManager(PaintManager):
    def initialize(self):

        # We generate the colored lines.
        # You can try to increase the values here.
        # If the number of primitives is too high, you may have errors.
        nprimitives = 20
        nsamples = 10000
        position, color = create_data(nprimitives, nsamples)
        
        self.create_dataset(PlotTemplate, nprimitives=nprimitives, 
            nsamples=nsamples, position=position, color=color)

show_basic_window(paint_manager=MyPaintManager, display_fps=True)
