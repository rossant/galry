from galry import *
import numpy as np
import numpy.random as rdn

class PointsPaintManager(PaintManager):
    def initialize(self):
        
        nprimitives = 100
        coordinates = .2 * rdn.randn(nprimitives, 4)
        colors = rdn.rand(nprimitives, 4)
        
        # add plot
        self.create_dataset(RectanglesTemplate, nprimitives=nprimitives)
        self.set_data(coordinates=coordinates, colors=colors)

if __name__ == '__main__':
    show_basic_window(paint_manager=PointsPaintManager)
