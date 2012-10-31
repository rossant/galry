from galry import *
import numpy as np
import numpy.random as rdn
import timeit
from mandelbrot2 import MandelbrotPaintManager, get_iterations

class MandelbrotInteractionManager(InteractionManager):
    def process_zoom_event(self, event, parameter):
        super(MandelbrotInteractionManager, self).process_zoom_event(event, parameter)
        if event == InteractionEvents.ZoomEvent:
            self.paint_manager.set_data(iterations=get_iterations(self.sx))
        
class MandelbrotWidget(GalryWidget):
    auto_zoom = QtCore.pyqtSignal(float, float, float, float)
    
    def initialize(self):
        self.constrain_ratio=True
        self.t = 0.
        self.t0 = timeit.default_timer()
        self.freq = 50.
        self.set_companion_classes(paint_manager=MandelbrotPaintManager,
                                    interaction_manager=MandelbrotInteractionManager)
        
    def initialized(self):
        # start simulation after initialization completes
        self.timer = QtCore.QTimer()
        self.timer.setInterval(1000. / self.freq)
        self.timer.timeout.connect(self.update)
        self.connect_events(self.auto_zoom, InteractionEvents.ZoomEvent)
        self.timer.start()
        
    def update(self):
        z = .75 / self.freq
        px, py = .55903686, .38220144
        self.auto_zoom.emit(z, px, z, py)
        self.t = timeit.default_timer() - self.t0
        if self.t >= 13:
            self.timer.stop()
        
    def showEvent(self, e):
        # start simulation when showing window
        self.timer.start()
        
    def hideEvent(self, e):
        # stop simulation when hiding window
        self.timer.stop()
        
if __name__ == '__main__':
    print "Zoom in!"
    window = show_basic_window(widget_class=MandelbrotWidget)
    