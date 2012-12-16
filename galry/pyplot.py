import numpy as np
# from collections import OrderedDict as odict

from galry import GalryWidget, show_basic_window, get_color, PaintManager,\
    InteractionManager, ordict
import galry.managers as mgs
import galry.visuals as vs

__all__ = ['figure', 'Figure', 'get_current_figure',
           'plot', 'text', 'rectangles', 'imshow', 'graph', 'mesh', 'barplot',
           'sprites',
           'visual',
           'axes', 'xlim', 'ylim',
           'grid', 'animate',
           'event', 'action',
           'show']

def get_marker_texture(marker, size=None):
    """Create a marker texture."""
    if size is None:
        size = 10.
    
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
        
    elif marker == '-':
        texture[size / 2, :, :] = 1
        
    elif marker == '|':
        texture[:, size / 2, :] = 1
        
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
    def create(figure, baseclass=None, update=None):
        if baseclass is None:
            baseclass = mgs.PlotPaintManager
        visuals = figure.visuals
        if not update:
            class MyPaintManager(baseclass):
                def initialize(self):
                    self.figure = figure
                    for name, (args, kwargs) in visuals.iteritems():
                        self.add_visual(*args, **kwargs)
                        
                def resizeGL(self, w, h):
                    super(MyPaintManager, self).resizeGL(w, h)
                    self.figure.size = w, h
                    
        else:
            class MyPaintManager(baseclass):
                def initialize(self):
                    for name, (args, kwargs) in visuals.iteritems():
                        self.add_visual(*args, **kwargs)
        return MyPaintManager

class InteractionManagerCreator(object):
    @staticmethod
    def create(figure, baseclass=None):
        if baseclass is None:
            baseclass = mgs.PlotInteractionManager
        handlers = figure.handlers
        processors = figure.processors
        class MyInteractionManager(baseclass):
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
    def create(figure, baseclass=None):
        if baseclass is None:
            baseclass = PlotBindings
        bindings = figure.bindings
        class MyBindings(baseclass):
            def initialize(self):
                super(MyBindings, self).initialize()
                for (args, kwargs) in bindings:
                    self.set(*args, **kwargs)
        return MyBindings
        

# Figure class
# ------------
class Figure(object):

    # Initialization methods
    # ----------------------
    def __init__(self, *args, **kwargs):
        self.visuals = ordict()
        self.handlers = ordict()
        self.processors = ordict()
        self.bindings = []
        self.viewbox = (None, None, None, None)
        
        self.constrain_ratio = None
        self.constrain_navigation = None
        self.display_fps = None
        self.activate3D = None
        self.antialiasing = None
        self.activate_grid = True
        self.activate_help = True
        self.animation_interval = None
        self.figsize = (GalryWidget.width, GalryWidget.height)

        self.pmclass = mgs.PlotPaintManager
        self.imclass = mgs.PlotInteractionManager
        self.bindingsclass = mgs.PlotBindings
        
        self.initialize(*args, **kwargs)
        
    def initialize(self, **kwargs):
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
                (self.get_visual_class(name) == vs.SpriteVisual) or
                (self.get_visual_class(name) == vs.BarVisual)
                
                ):
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
            if opt and opt[0] in ',.+-|xo':
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
        
    def barplot(self, *args, **kwargs):
        self.add_visual(vs.BarVisual, *args, **kwargs)
        
    def text(self, *args, **kwargs):
        self.add_visual(vs.TextVisual, *args, **kwargs)
        
    def rectangles(self, *args, **kwargs):
        self.add_visual(vs.RectanglesVisual, *args, **kwargs)
    
    def sprites(self, *args, **kwargs):
        self.add_visual(vs.SpriteVisual, *args, **kwargs)
       
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
        
    def mesh(self, *args, **kwargs):
        self.pmclass = mgs.MeshPaintManager
        self.imclass = mgs.MeshInteractionManager
        self.antialiasing = True
        self.bindingsclass = mgs.MeshBindings
        self.add_visual(vs.MeshVisual, *args, **kwargs)
    
    def visual(self, visualcls, *args, **kwargs):
        self.add_visual(visualcls, *args, **kwargs)
    
    def grid(self, *args, **kwargs):
        # TODO: do not add new grid visual but activate the existing one
        self.add_visual(vs.GridVisual, *args, **kwargs)
        self.add_event_processor(vs.GridEventProcessor)
        
        
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
            event = getattr(callback, '__name__', 'CustomEvent%d' % len(self.bindings))
            # we bind the action to that event
            # we also pass the full User Action Parameters object to the
            # callback
            if 'param_getter' not in kwargs:
                kwargs['param_getter'] = lambda p: p
            self.action(action, event, *args, **kwargs)
            # and we bind that event to the specified callback
            self.event(event, callback)
        else:
            args = (action, event) + args
            # self.add_binding(event, method)
            self.bindings.append((args, kwargs))
        
    def animate(self, method, dt=None):
        if dt is None:
            dt = .02
        self.animation_interval = dt
        self.event('Animate', method)
        
        
    # Rendering methods
    # -----------------
    def show(self):
        self.update_normalization()
        pm = PaintManagerCreator.create(self, self.pmclass)
        im = InteractionManagerCreator.create(self, self.imclass)
        bindings = BindingCreator.create(self, self.bindingsclass)
        window = show_basic_window(
            paint_manager=pm,
            interaction_manager=im,
            bindings=bindings,
            constrain_ratio=self.constrain_ratio,
            constrain_navigation=self.constrain_navigation,
            display_fps=self.display_fps,
            activate3D=self.activate3D,
            antialiasing=self.antialiasing,
            activate_grid=self.activate_grid,
            activate_help=self.activate_help,
            animation_interval=self.animation_interval,
            size=self.figsize,
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

    
# Visual methods
# --------------
def plot(*args, **kwargs):
    fig = get_current_figure()
    fig.plot(*args, **kwargs)
    
def barplot(*args, **kwargs):
    fig = get_current_figure()
    fig.barplot(*args, **kwargs)
    
def text(*args, **kwargs):
    fig = get_current_figure()
    fig.text(*args, **kwargs)
    
def rectangles(*args, **kwargs):
    fig = get_current_figure()
    fig.rectangles(*args, **kwargs)
    
def sprites(*args, **kwargs):
    fig = get_current_figure()
    fig.sprites(*args, **kwargs)
    
def imshow(*args, **kwargs):
    fig = get_current_figure()
    fig.imshow(*args, **kwargs)

def graph(*args, **kwargs):
    fig = get_current_figure()
    fig.graph(*args, **kwargs)
    
def mesh(*args, **kwargs):
    fig = get_current_figure()
    fig.mesh(*args, **kwargs)
    
def visual(*args, **kwargs):
    fig = get_current_figure()
    fig.visual(*args, **kwargs)
    

    
# Axes methods
# ------------
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
    
    
# Event methods
# -------------
def event(*args, **kwargs):
    fig = get_current_figure()
    fig.event(*args, **kwargs)
    
def action(*args, **kwargs):
    fig = get_current_figure()
    fig.action(*args, **kwargs)
    
def animate(*args, **kwargs):
    fig = get_current_figure()
    fig.animate(*args, **kwargs)
    
    
def show(*args, **kwargs):
    fig = get_current_figure()
    fig.show(*args, **kwargs)



    