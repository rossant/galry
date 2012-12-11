from galrywidget import GalryWidget, show_basic_window
import visuals as vs
from paintmanager import PaintManager
from collections import OrderedDict as odict

__all__ = ['figure', 'Figure', 'get_current_figure',
           'plot', 'text', 'rectangles', 'imshow',
           'show']


class PaintManagerCreator(object):
    @staticmethod
    def create(figure):
        visuals = figure.visuals
        class MyPaintManager(PaintManager):
            def initialize(self):
                for name, (args, kwargs) in visuals.iteritems():
                    self.add_visual(*args, **kwargs)
        return MyPaintManager


class Figure(object):

    # Initialization methods
    # ----------------------
    def __init__(self, *args, **kwargs):
        self.visuals = odict()
        self.viewbox = (None, None, None, None)
        self.initialize(*args, **kwargs)
        
    def initialize(self, constrain_ratio=False):
        self.constrain_ratio = constrain_ratio
    
    
    # Internal methods
    # ----------------
    def add_visual(self, *args, **kwargs):
        name = kwargs.get('name', 'visual%d' % len(self.visuals))
        self.visuals[name] = (args, kwargs)
    
    def get_visual_class(self, name):
        return self.visuals[name][0][0]
        
    def update_visual(self, name, **kwargs):
        self.visuals[name][1].update(kwargs)
        
        
    # Normalization methods
    # ---------------------
    def axes(self, *viewbox):
        self.viewbox = viewbox
    
    def xlim(self, x0, x1):
        self.axes(x0, None, x1, None)
    
    def ylim(self, y0, y1):
        self.axes(None, y0, None, y1)
    
    def update_normalization(self):
        for name, visual in self.visuals.iteritems():
            if self.get_visual_class(name) == vs.PlotVisual:
                self.update_visual(name, viewbox=self.viewbox)

        
    # Visual methods
    # --------------
    def plot(self, *args, **kwargs):
        # by default in the high level interface: activate normalization
        # print kwargs
        # if 'viewbox' not in kwargs:
            # kwargs['viewbox'] = 37#(None, None, None, None)
        # print kwargs
        self.add_visual(vs.PlotVisual, *args, **kwargs)
        
    def text(self, *args, **kwargs):
        self.add_visual(vs.TextVisual, *args, **kwargs)
        
    def rectangles(self, *args, **kwargs):
        self.add_visual(vs.RectanglesVisual, *args, **kwargs)
        
    def imshow(self, *args, **kwargs):
        self.add_visual(vs.TextureVisual, *args, **kwargs)
        
        
    # Rendering methods
    # -----------------
    def show(self):
        self.update_normalization()
        pm = PaintManagerCreator.create(self)
        return show_basic_window(paint_manager=pm,
            constrain_ratio=self.constrain_ratio)






def figure(*args, **kwargs):
    fig = Figure(*args, **kwargs)
    
    return fig

    
    
# Default figure in the namespace
# -------------------------------
_FIGURE = None
def get_current_figure():
    global _FIGURE
    if not _FIGURE:
        _FIGURE = figure()
    return _FIGURE

    

def plot(*args, **kwargs):
    fig = get_current_figure()
    fig.plot(*args, **kwargs)
    
def text(*args, **kwargs):
    fig = get_current_figure()
    fig.text(*args, **kwargs)
    
def rectangles(*args, **kwargs):
    fig = get_current_figure()
    fig.rectangles(*args, **kwargs)
    
def imshow(*args, **kwargs):
    fig = get_current_figure()
    fig.imshow(*args, **kwargs)
    
def show(*args, **kwargs):
    fig = get_current_figure()
    fig.show(*args, **kwargs)
    
    
    
    
    
    
    
    
    