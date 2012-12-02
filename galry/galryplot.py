"""Temporary class used for the IPython notebook. It will disappear when
the high level interface is ready."""

import numpy as np
from galry import *

class GalryPlot(object):
    def __init__(self, x=None, y=None):
        n = 2
        if x is None:
            x = np.linspace(-1., 1., n)
        if y is None:
            y = np.zeros(n)
        data = np.empty((len(x), 2), dtype=np.float32)
        data[:,0] = x
        data[:,1] = y
        self.data = data
        self.scene_creator = SceneCreator()
        self.scene_creator.add_visual(PlotVisual, x=x, y=y)
        
    def serialize(self, **kwargs):
        return self.scene_creator.serialize(**kwargs)
        
if __name__ == '__main__':
    pl = GalryPlot()
    print pl.serialize()
    
    