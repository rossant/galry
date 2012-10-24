from galry import *
import numpy as np

class SinusPaintManager(PaintManager):
    def initialize(self):
        # define two functions on [-1, 1]
        x = np.linspace(-1., 1., 1000)
        y1 = 0.5 * np.sin(20 * x)
        y2 = 0.5 * np.cos(20 * x)
        # add two plots with two different colors
        self.add_plot(x, y1, (1,0,0), primitive_type=PrimitiveType.LineStrip)
        self.add_plot(x, y2, (1,1,0), primitive_type=PrimitiveType.LineStrip)

if __name__ == '__main__':
    # create window
    window = show_basic_window(paint_manager=SinusPaintManager)
    