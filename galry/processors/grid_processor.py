import inspect
from collections import OrderedDict as odict
import numpy as np
from processor import EventProcessor
from galry import Manager, TextVisual, get_color


__all__ = ['GridEventProcessor']


class GridEventProcessor(EventProcessor):
    def initialize(self):
        self.register('Initialize', self.update_axes)
        self.register('Pan', self.update_axes)
        self.register('Zoom', self.update_axes)
        self.register('Reset', self.update_axes)
        self.register(None, self.update_axes)
        
    def update_axes(self, parameter):
        viewbox = self.get_processor('navigation').get_viewbox()
        text, coordinates, n = get_ticks_text(*viewbox)
        
        t = "".join(text)
        n1 = len("".join(text[:n]))
        n2 = len("".join(text[n:]))
        
        axis = np.zeros(n1+n2)
        axis[n1:] = 1
        
        self.set_data(visual='ticks_text', text=text,
            coordinates=coordinates,
            axis=axis)
            
            