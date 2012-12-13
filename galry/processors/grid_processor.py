import inspect
from collections import OrderedDict as odict
import numpy as np
from processor import EventProcessor


__all__ = ['GridEventProcessor']


# http://books.google.co.uk/books?id=fvA7zLEFWZgC&lpg=PA61&hl=fr&pg=PA62#v=onepage&q&f=false
def nicenum(x, round=False):
    e = np.floor(np.log10(x))
    f = x / 10 ** e
    if round:
        if f < 1.5:
            nf = 1.
        elif f < 3:
            nf = 2.
        elif f < 7.:
            nf = 5.
        else:
            nf = 10.
    else:
        if f <= 1:
            nf = 1.
        elif f <= 2:
            nf = 2.
        elif f <= 5.:
            nf = 5.
        else:
            nf = 10.
    return nf * 10 ** e
    
def get_ticks(x0, x1):
    nticks = 10
    r = nicenum(x1 - x0, False)
    d = nicenum(r / (nticks - 1), True)
    g0 = np.floor(x0 / d) * d
    g1 = np.ceil(x1 / d) * d
    nfrac = int(max(-np.floor(np.log10(d)), 0))
    return np.arange(g0, g1 + .5 * d, d), nfrac
  
def format_number(x, nfrac=None):
    if nfrac is None:
        nfrac = 2
    
    if np.abs(x) < 1e-15:
        return "0"
        
    elif np.abs(x) > 100.001:
        return "%.2e" % x
        
    if nfrac <= 2:
        return "%.2f" % x
    else:
        return ("%." + str(nfrac - 1) + "e") % x

def get_ticks_text(x0, y0, x1, y1):
    ticksx, nfracx = get_ticks(x0, x1)
    ticksy, nfracy = get_ticks(y0, y1)
    n = len(ticksx)
    text = [format_number(x, nfracx) for x in ticksx]
    text += [format_number(x, nfracy) for x in ticksy]
    # position of the ticks
    coordinates = np.zeros((len(text), 2))
    coordinates[:n, 0] = ticksx
    coordinates[n:, 1] = ticksy
    return text, coordinates, n
    
    
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
        
        # here: coordinates contains positions centered on the static
        # xy=0 axes of the screen
        
        position = np.repeat(coordinates, 2, axis=0)
        position[:2 * n:2,1] = -1
        position[1:2 * n:2,1] = 1
        position[2 * n::2,0] = -1
        position[2 * n + 1::2,0] = 1
        
        axis = np.zeros(len(position))
        axis[2 * n:] = 1
        
        # print position
        
        self.set_data(visual='grid_lines', position=position, axis=axis)
        
        
        
        coordinates[n:, 0] = -.95
        coordinates[:n, 1] = -.95
    
        t = "".join(text)
        n1 = len("".join(text[:n]))
        n2 = len("".join(text[n:]))
        
        axis = np.zeros(n1+n2)
        axis[n1:] = 1
        
        self.set_data(visual='grid_text', text=text,
            coordinates=coordinates,
            axis=axis)
            
            