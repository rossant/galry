from galrywidget import GalryWidget, show_basic_window
import visuals as vs
from paintmanager import PaintManager
from interactionmanager import InteractionManager
from bindingmanager import DefaultBindingSet
from collections import OrderedDict as odict

__all__ = ['figure', 'Figure', 'get_current_figure',
           'plot', 'text', 'rectangles', 'imshow',
           'event', 'action',
           'show']


# Manager creator classes
# -----------------------
class PaintManagerCreator(object):
    @staticmethod
    def create(figure):
        visuals = figure.visuals
        class MyPaintManager(PaintManager):
            def initialize(self):
                for name, (args, kwargs) in visuals.iteritems():
                    self.add_visual(*args, **kwargs)
        return MyPaintManager

class InteractionManagerCreator(object):
    @staticmethod
    def create(figure):
        handlers = figure.handlers
        class MyInteractionManager(InteractionManager):
            def initialize(self):
                # use this to pass this Figure instance to the handler function
                # as a first argument (in EventProcessor.process)
                self.figure = figure
                for event, method in handlers.iteritems():
                    self.register(event, method)
        return MyInteractionManager

class BindingCreator(object):
    @staticmethod
    def create(figure):
        bindings = figure.bindings
        class MyBindings(DefaultBindingSet):
            def extend(self):
                for (args, kwargs) in bindings:
                    self.set(*args, **kwargs)
        return MyBindings
        

# Figure class
# ------------
class Figure(object):

    # Initialization methods
    # ----------------------
    def __init__(self, *args, **kwargs):
        self.visuals = odict()
        self.handlers = odict()
        self.bindings = []
        self.viewbox = (None, None, None, None)
        self.initialize(*args, **kwargs)
        
    def initialize(self, constrain_ratio=False):
        self.constrain_ratio = constrain_ratio
    
    
    # Internal visual methods
    # -----------------------
    def add_visual(self, *args, **kwargs):
        name = kwargs.get('name', 'visual%d' % len(self.visuals))
        self.visuals[name] = (args, kwargs)
    
    def get_visual_class(self, name):
        return self.visuals[name][0][0]
        
    def update_visual(self, name, **kwargs):
        self.visuals[name][1].update(kwargs)
        
        
    # # Internal interaction methods
    # # ----------------------------
    # def add_handler(self, event, method):
        # self.handlers[event] = method
        
    # def add_binding(self, *args, **kwargs):
        # self.bindings.add((args, kwargs))
        
    
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

        
    # Public visual methods
    # ---------------------
    def plot(self, *args, **kwargs):
        self.add_visual(vs.PlotVisual, *args, **kwargs)
        
    def text(self, *args, **kwargs):
        self.add_visual(vs.TextVisual, *args, **kwargs)
        
    def rectangles(self, *args, **kwargs):
        self.add_visual(vs.RectanglesVisual, *args, **kwargs)
        
    def imshow(self, *args, **kwargs):
        self.add_visual(vs.TextureVisual, *args, **kwargs)
        
        
    # Public interaction methods
    # --------------------------
    def event(self, event, method):
        # self.add_handler(event, method)
        self.handlers[event] = method
        
    def action(self, action, event, *args, **kwargs):
        # first case: event is a function or a method, and directly bind the
        # action to that function
        if not isinstance(event, basestring):
            callback = event
            # we create a custom event
            event = 'MyEvent%d' % len(self.bindings)
            # we bind the action to that event
            # we also pass the full User Action Parameters object to the
            # callback
            self.action(action, event, param_getter=lambda p: p)
            # and we bind that event to the specified callback
            self.event(event, callback)
        else:
            args = (action, event) + args
            # self.add_binding(event, method)
            self.bindings.append((args, kwargs))
        
        
    # Rendering methods
    # -----------------
    def show(self):
        self.update_normalization()
        pm = PaintManagerCreator.create(self)
        im = InteractionManagerCreator.create(self)
        bindings = BindingCreator.create(self)
        return show_basic_window(
            paint_manager=pm,
            interaction_manager=im,
            bindings=bindings,
            constrain_ratio=self.constrain_ratio)


# Public figure methods
# ---------------------
def figure(*args, **kwargs):
    fig = Figure(*args, **kwargs)
    
    return fig

# Default figure in the namespace
_FIGURE = None
def get_current_figure():
    global _FIGURE
    if not _FIGURE:
        _FIGURE = figure()
    return _FIGURE

    
# Public methods
# --------------
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
    
def event(*args, **kwargs):
    fig = get_current_figure()
    fig.event(*args, **kwargs)
    
def action(*args, **kwargs):
    fig = get_current_figure()
    fig.action(*args, **kwargs)
    
def show(*args, **kwargs):
    fig = get_current_figure()
    fig.show(*args, **kwargs)



    