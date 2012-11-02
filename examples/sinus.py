from galry import *
import numpy as np

class SinusPaintManager(PaintManager):
    def initialize(self):
        # define two functions on [-1, 1]
        x = np.linspace(-1., 1., 1000)
        y1 = 0.5 * np.sin(20 * x)
        y2 = 0.5 * np.cos(20 * x)
        positions = np.empty((2 * len(x), 2))
        positions[:1000,0] = x
        positions[1000:,0] = x
        positions[:1000,1] = y1
        positions[1000:,1] = y2
        # add two plots with two different colors
        
        colors = np.ones((2, 3))
        colors[0,1:3] = 0
        colors[1,2] = 0
        
        self.create_dataset(PlotTemplate,
            nprimitives=2,
            nsamples=1000,
            position=positions,
            color=colors)

if __name__ == '__main__':
    # create window
    window = show_basic_window(paint_manager=SinusPaintManager)
    