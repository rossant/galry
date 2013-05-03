import inspect
# from collections import OrderedDict as odict
import numpy as np
from processor import EventProcessor
from galry import DataNormalizer

NTICKS = 10

__all__ = ['GridEventProcessor']


# http://books.google.co.uk/books?id=fvA7zLEFWZgC&lpg=PA61&hl=fr&pg=PA62#v=onepage&q&f=false
def nicenum(x, round=False):
    e = np.floor(np.log10(x))
    f = x / 10 ** e
    eps = 1e-6
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
        if f < 1 - eps:
            nf = 1.
        elif f < 2 - eps:
            nf = 2.
        elif f < 5 - eps:
            nf = 5.
        else:
            nf = 10.
    return nf * 10 ** e
    
def get_ticks(x0, x1):
    nticks = NTICKS
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
        return "%.3e" % x
        
    if nfrac <= 2:
        return "%.2f" % x
    else:
        nfrac = nfrac + int(np.log10(np.abs(x)))
        return ("%." + str(nfrac) + "e") % x

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
        self.register('Animate', self.update_axes)
        self.register(None, self.update_axes)
        
    def update_axes(self, parameter):
        nav = self.get_processor('navigation')
        # print nav
        if not nav:
            return
        
        viewbox = nav.get_viewbox()
        
        # nvb = nav.normalization_viewbox
        nvb = getattr(self.parent.paint_manager, 'normalization_viewbox', None)
        # print nvb
        # initialize the normalizer
        if nvb is not None:
            if not hasattr(self, 'normalizer'):
                # normalization viewbox
                self.normalizer = DataNormalizer()
                self.normalizer.normalize(nvb)
            x0, y0, x1, y1 = viewbox
            x0 = self.normalizer.unnormalize_x(x0)
            y0 = self.normalizer.unnormalize_y(y0)
            x1 = self.normalizer.unnormalize_x(x1)
            y1 = self.normalizer.unnormalize_y(y1)
            viewbox = (x0, y0, x1, y1)
            # print nvb, viewbox
        
        text, coordinates, n = get_ticks_text(*viewbox)
        
        if nvb is not None:
            coordinates[:,0] = self.normalizer.normalize_x(coordinates[:,0])
            coordinates[:,1] = self.normalizer.normalize_y(coordinates[:,1])
        
        
        # here: coordinates contains positions centered on the static
        # xy=0 axes of the screen
        position = np.repeat(coordinates, 2, axis=0)
        position[:2 * n:2,1] = -1
        position[1:2 * n:2,1] = 1
        position[2 * n::2,0] = -1
        position[2 * n + 1::2,0] = 1
        
        axis = np.zeros(len(position))
        axis[2 * n:] = 1
        
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
            