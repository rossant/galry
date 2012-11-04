from galry import *
import numpy as np
import numpy.random as rdn
import timeit
from mandelbrot2 import MandelbrotPaintManager, get_iterations

class MandelbrotInteractionManager(InteractionManager):
    def zoom(self, parameter):
        super(MandelbrotInteractionManager, self).zoom(parameter)
        self.paint_manager.set_data(iterations=get_iterations(self.sx))
    
class AutoMandelbrotPaintManager(MandelbrotPaintManager):
    def update_callback(self):
        z = .75 * self.parent.dt
        px, py = .55903686, .38220144
        self.interaction_manager.zoom((z, px, z, py))
        if self.t >= 13:
            self.parent.stop_timer()
            
if __name__ == '__main__':
    window = show_basic_window(paint_manager=AutoMandelbrotPaintManager,
        interaction_manager=MandelbrotInteractionManager,
        constrain_ratio=True,
        update_interval=.05)
    