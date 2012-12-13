import numpy as np
from collections import OrderedDict as odict

from galry import GalryWidget, show_basic_window, get_color, PaintManager,\
    InteractionManager, DefaultBindingSet
import galry.visuals as vs

__all__ = ['figure', 'Figure', 'get_current_figure',
           'plot', 'text', 'rectangles', 'imshow', 'graph',
           'axes', 'xlim', 'ylim',
           'grid',
           'event', 'action',
           'show']

def get_marker_texture(marker, size=None):
    """Create a marker texture."""
    
    if np.mod(size, 2) == 0:
        size += 1
        
    if marker == '.':
        marker = ','
        size = 5.
    if size is None:
        size = 5.
    
    texture = np.zeros((size, size, 4))
    
    if marker == ',':
        texture[:] = 1
        
    elif marker == '+':
        texture[size / 2, :, :] = 1
        texture[:, size / 2, :] = 1
        
    elif marker == 'x':
        texture[range(size), range(size), :] = 1
        texture[range(size - 1, -1, -1), range(size), :] = 1
        
    elif marker == 'o':
        # fill with white
        texture[:, :, :-1] = 1
        x = np.linspace(-1., 1., size)
        X, Y = np.meshgrid(x, x)
        R = X ** 2 + Y ** 2
        R = np.minimum(1, 3 * np.exp(-3*R))
        # disc-shaped alpha channel
        texture[:,:,-1] = R
        
    
    return texture


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
        processors = figure.processors
        class MyInteractionManager(InteractionManager):
            def initialize(self):
                # use this to pass this Figure instance to the handler function
                # as a first argument (in EventProcessor.process)
                self.figure = figure
                # add all handlers
                for event, method in handlers.iteritems():
                    self.register(event, method)
                # add all event processors
                for name, (args, kwargs) in processors.iteritems():
                    self.add_processor(*args, **kwargs)
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
        self.processors = odict()
        self.bindings = []
        self.viewbox = (None, None, None, None)
        
        self.constrain_ratio = None
        self.constrain_navigation = None
        self.display_fps = None
        self.activate_grid = True
        self.activate_help = True
        
        self.initialize(*args, **kwargs)
        
    def initialize(self, **kwargs
            # constrain_ratio=False, constrain_navigation=False,
            # display_fps=None
            ):
        # self.constrain_ratio = constrain_ratio
        # self.constrain_navigation = constrain_navigation
        # self.display_fps = display_fps
        for name, value in kwargs.iteritems():
            setattr(self, name, value)
    
    
    # Internal visual methods
    # -----------------------
    def add_visual(self, *args, **kwargs):
        name = kwargs.get('name', 'visual%d' % len(self.visuals))
        self.visuals[name] = (args, kwargs)
    
    def get_visual_class(self, name):
        return self.visuals[name][0][0]
        
    def update_visual(self, name, **kwargs):
        self.visuals[name][1].update(kwargs)
        
        
    # Internal interaction methods
    # ----------------------------
    def add_event_processor(self, *args, **kwargs):
        name = kwargs.get('name', 'processor%d' % len(self.processors))
        self.processors[name] = (args, kwargs)
        
        
    # Normalization methods
    # ---------------------
    def axes(self, *viewbox):
        if len(viewbox) == 1:
            viewbox = viewbox[0]
        x0, x1, y0, y1 = viewbox
        self.viewbox = (x0, y0, x1, y1)
    
    def xlim(self, x0, x1):
        self.axes(x0, x1, None, None)
    
    def ylim(self, y0, y1):
        self.axes(None, None, y0, y1)
    
    def update_normalization(self):
        for name, visual in self.visuals.iteritems():
            if ((self.get_visual_class(name) == vs.PlotVisual) or
                (self.get_visual_class(name) == vs.SpriteVisual)):
                self.update_visual(name, viewbox=self.viewbox)

        
    # Public visual methods
    # ---------------------
    def plot(self, *args, **kwargs):
        
        # deal with special string argument containing options
        lenargs = len(args)
        opt = ''
        # we look for the index in args such that args[i] is a string
        for i in xrange(lenargs):
            if isinstance(args[i], basestring):
                opt = args[i]
                break
        if opt:
            # we remove the options from the arguments
            l = list(args)
            l.remove(opt)
            args = tuple(l)
            kwargs['options'] = opt
        
        # process marker type, 'o' or 'or'
        marker = kwargs.pop('marker', kwargs.pop('m', None))
        if marker is None:
            if opt and opt[0] in ',.+xo':
                marker = opt[0]
        if marker is not None:
            cls = vs.SpriteVisual
            texsize = kwargs.pop('marker_size', kwargs.pop('ms', None))
            kwargs['texture'] = get_marker_texture(marker, texsize)
            kwargs.pop('options', None)
            # process marker color in options
            if 'color' not in kwargs and len(opt) == 2:
                kwargs['color'] = get_color(opt[1])
        else:
            cls = vs.PlotVisual
        
        self.add_visual(cls, *args, **kwargs)
        
    def text(self, *args, **kwargs):
        self.add_visual(vs.TextVisual, *args, **kwargs)
        
    def rectangles(self, *args, **kwargs):
        self.add_visual(vs.RectanglesVisual, *args, **kwargs)
        
    def imshow(self, *args, **kwargs):
        filter = kwargs.pop('filter', None)
        if filter:
            kwargs.update(
                mipmap=True,
                minfilter='LINEAR_MIPMAP_NEAREST',
                magfilter='LINEAR',)
        self.add_visual(vs.TextureVisual, *args, **kwargs)
        
    def graph(self, *args, **kwargs):
        self.add_visual(vs.GraphVisual, *args, **kwargs)
        
        
        
    def grid(self, *args, **kwargs):
        self.add_visual(vs.GridVisual, *args, **kwargs)
        self.add_event_processor(vs.GridEventProcessor)
        
        
    def set_data(self, *args, **kwargs):
        self.paint_manager.set_data(self, *args, **kwargs)
        
        
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
        window = show_basic_window(
            paint_manager=pm,
            interaction_manager=im,
            bindings=bindings,
            constrain_ratio=self.constrain_ratio,
            constrain_navigation=self.constrain_navigation,
            display_fps=self.display_fps,
            activate_grid=self.activate_grid,
            activate_help=self.activate_help,
            )
        return window
            

# Public figure methods
# ---------------------
def figure(*args, **kwargs):
    fig = Figure(*args, **kwargs)
    global _FIGURE
    _FIGURE = fig
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

def graph(*args, **kwargs):
    fig = get_current_figure()
    fig.graph(*args, **kwargs)
    
    
def grid(*args, **kwargs):
    fig = get_current_figure()
    fig.grid(*args, **kwargs)
    
def axes(*args, **kwargs):
    fig = get_current_figure()
    fig.axes(*args, **kwargs)
    
def xlim(*args, **kwargs):
    fig = get_current_figure()
    fig.xlim(*args, **kwargs)
    
def ylim(*args, **kwargs):
    fig = get_current_figure()
    fig.ylim(*args, **kwargs)
    
    
def event(*args, **kwargs):
    fig = get_current_figure()
    fig.event(*args, **kwargs)
    
def action(*args, **kwargs):
    fig = get_current_figure()
    fig.action(*args, **kwargs)
    
    
def show(*args, **kwargs):
    fig = get_current_figure()
    fig.show(*args, **kwargs)



    