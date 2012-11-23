from galry import *
import numpy as np
import numpy.random as rdn
from mandelbrot import MandelbrotVisual

def get_iterations(zoom=1):
    return int(500 * np.log(1 + zoom))

class MandelbrotPaintManager(PaintManager):
    def initialize(self):
        # create the textured rectangle and specify the shaders
        self.add_visual(MandelbrotVisual, iterations=get_iterations())

class MandelbrotInteractionManager(InteractionManager):
    def process_zoom_event(self, event, parameter):
        super(MandelbrotInteractionManager, self).process_zoom_event(event, parameter)
        if event == InteractionEvents.ZoomEvent:
            self.paint_manager.set_data(iterations=get_iterations(self.sx))
        
if __name__ == '__main__':
    print "Zoom in!"
    window = show_basic_window(paint_manager=MandelbrotPaintManager,
                               interaction_manager=MandelbrotInteractionManager,
                               constrain_ratio=True,
                               constrain_navigation=True,
                               )
    