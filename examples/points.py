from galry import *
import numpy.random as rdn

class PointsPaintManager(PaintManager):
    def initialize(self):
        # generate random points
        positions = .25 * rdn.randn(100000, 2)
        # add plot
        self.create_dataset(PlotTemplate, size=len(positions))
        self.set_data(position=positions)

if __name__ == '__main__':
    show_basic_window(paint_manager=PointsPaintManager)
