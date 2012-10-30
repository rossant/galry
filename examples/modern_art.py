from galry import *
import numpy.random as rdn

class ArtPaintManager(PaintManager):
    def initialize(self):
        # random positions
        positions = .25 * rdn.randn(1000, 2)
        # random colors
        colors = rdn.rand(len(positions),4)
        # add plot with triangles, 3 consecutive points define a single triangle
        self.create_dataset(PlotTemplate, size=len(positions), single_color=False,
                      primitive_type=PrimitiveType.Triangles)
        self.set_data(position=positions, color=colors)

if __name__ == '__main__':
    # create window
    window = show_basic_window(paint_manager=ArtPaintManager,
                                constrain_ratio=True,
                                antialiasing=True)