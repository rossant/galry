import numpy as np
from galry import *

class GalryPlot(object):
    def __init__(self, x=None, y=None):
        if x is None:
            x = np.linspace(-1., 1., 100000)
        if y is None:
            y = np.zeros(100000)
        data = np.empty((len(x), 2), dtype=np.float32)
        data[:,0] = x
        data[:,1] = y
        self.data = data
        
    def get_widget(self):
        data = self.data
        class MyPM(PaintManager):
            def initialize(self):
                self.create_dataset(PlotTemplate, position=data,
                     color=(1.,1.,0.,1.))
        return create_custom_widget(paint_manager=MyPM)
        
if __name__ == '__main__':
    pl = GalryPlot()
    w = pl.get_widget()()
    w.initializeGL()
    