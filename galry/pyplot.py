import numpy as np
# from collections import OrderedDict as odict
import inspect

from galry import GalryWidget, show_basic_window, get_color, PaintManager,\
    InteractionManager, ordict, get_next_color
import galry.managers as mgs
import galry.processors as ps
import galry.visuals as vs

__all__ = ['figure', 'Figure', 'get_current_figure',
           'plot', 'text', 'rectangles', 'imshow', 'graph', 'mesh', 'barplot', 'surface',
           'sprites',
           'visual',
           'axes', 'xlim', 'ylim',
           'grid', 'animate',
           'event', 'action',
           'framebuffer',
           'show']

def get_marker_texture(marker, size=None):
    """Create a marker texture."""
    # if size is None:
        # size = 1
        
    if marker == '.':
        marker = ','
        if size is None:
            size = 2
    
    if size is None:
        if marker == ',':
            size = 1
        else:
            size = 5
        
    texture = np.zeros((size, size, 4))
    
    if marker == ',':
        texture[:] = 1
        
    elif marker == '+':
        # force odd number
        size -= (np.mod(size, 2) - 1)
        texture[size / 2, :, :] = 1
        texture[:, size / 2, :] = 1
        
    elif marker == 'x':
        # force even number
        size -= (np.mod(size, 2))
        texture[range(size), range(size), :] = 1
        texture[range(size - 1, -1, -1), range(size), :] = 1
        
    elif marker == '-':
        texture[size / 2, :, :] = 1
        
    elif marker == '|':
        texture[:, size / 2, :] = 1
        
    elif marker == 'o':
        # force even number
        size -= (np.mod(size, 2))
        # fill with white
        texture[:, :, :-1] = 1
        x = np.linspace(-1., 1., size)
        X, Y = np.meshgrid(x, x)
        R = X ** 2 + Y ** 2
        R = np.minimum(1, 20 * np.exp(-8*R))
        # disc-shaped alpha channel
        texture[:size,:size,-1] = R
    
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
                    self.normalization_viewbox = figure.viewbox
                    for name, (args, kwargs) in visuals.iteritems():
                        self.add_visual(*args, **kwargs)
                        
                def resizeGL(self, w, h):
                    super(MyPaintManager, self).resizeGL(w, h)
                    self.figure.size = w, h
                    
        else:
            class MyPaintManager(baseclass):
                def initialize(self):
                    self.normalization_viewbox = figure.viewbox
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
            # def initialize_default(self,
                # constrain_navigation=None,
                # normalization_viewbox=None):
                # super(MyInteractionManager, self).initialize_default(
                    # constrain_navigation=constrain_navigation,
                    # normalization_viewbox=figure.viewbox)
            
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
        self.show_grid = False
        self.activate_help = True
        self.momentum = False
        self.figsize = (GalryWidget.w, GalryWidget.h)
        self.toolbar = True
        self.autosave = None
        self.autodestruct = None
        
        self.pmclass = kwargs.pop('paint_manager', mgs.PlotPaintManager)
        self.imclass = kwargs.pop('interaction_manager', mgs.PlotInteractionManager)
        self.bindingsclass = kwargs.pop('bindings', mgs.PlotBindings)
        
        self.initialize(*args, **kwargs)
        
        if self.momentum:
            self.animation_interval = .01
        else:
            self.animation_interval = None
        
    def initialize(self, **kwargs):
        for name, value in kwargs.iteritems():
            setattr(self, name, value)
    
    
    # Internal visual methods
    # -----------------------
    def add_visual(self, *args, **kwargs):
        name = kwargs.get('name', 'visual%d' % len(self.visuals))
        
        # give the autocolor (colormap index) only if it
        # is requested
        _args, _, _, _ = inspect.getargspec(args[0].initialize)
        if 'autocolor' in _args:
            if kwargs.get('color', None) is None:
                kwargs['autocolor'] = len(self.visuals)
            
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
        """Set the axes with (x0, y0, x1, y1)."""
        if len(viewbox) == 1:
            viewbox = viewbox[0]
        x0, y0, x1, y1 = viewbox
        px0, py0, px1, py1 = self.viewbox
        if x0 is None:
            x0 = px0
        if x1 is None:
            x1 = px1
        if y0 is None:
            y0 = py0
        if y1 is None:
            y1 = py1
        self.viewbox = (x0, y0, x1, y1)
    
    def xlim(self, x0, x1):
        """Set the x limits x0 and x1."""
        self.axes(x0, None, x1, None)
    
    def ylim(self, y0, y1):
        """Set the y limits y0 and y1."""
        self.axes(None, y0, None, y1)
    
        
    # Public visual methods
    # ---------------------
    def plot(self, *args, **kwargs):
        """Plot lines, curves, scatter plots, or any sequence of basic
        OpenGL primitives.
        
        Arguments:
        
          * x, y: 1D vectors of the same size with point coordinates, or
            2D arrays where each row is plotted as an independent plot.
            If only x is provided, then it contains the y coordinates and the
            x coordinates are assumed to be linearly spaced.
          * options: a string with shorcuts for the options: color and marker.
            The color can be any char among: `rgbycmkw`.
            The marker can be any char among: `,.+-|xo`. 
          * color: the color of the line(s), or a list/array of colors for each 
            independent primitive.
          * marker, or m: the type of the marker as a char, or a NxMx3 texture.
          * marker_size, or ms: the size of the marker.
          * thickness: None by default, or the thickness of the line.
          * primitive_type: the OpenGL primitive type of the visual. Can be:
          
              * `LINES`: a segment is rendered for each pair of successive
                points
              * `LINE_STRIP`: a sequence of segments from one point to the
                next.
              * `LINE_LOOP`: like `LINE_STRIP` but closed.
              * `POINTS`: each point is rendered as a pixel.
              * `TRIANGLES`: each successive triplet of points is rendered as
                a triangle.
              * `TRIANGLE_STRIP`: one triangle is rendered from a point to the
                next (i.e. successive triangles share two vertices out of
                three).
              * `TRIANGLE_FAN`: the first vertex is shared by all triangles.
        
        """
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
            # marker string
            if isinstance(marker, basestring): 
                kwargs['texture'] = get_marker_texture(marker, texsize)
            # or custom texture marker
            else:
                kwargs['texture'] = marker
            kwargs.pop('options', None)
            # process marker color in options
            if 'color' not in kwargs and len(opt) == 2:
                kwargs['color'] = get_color(opt[1])
        else:
            cls = vs.PlotVisual
        
        self.add_visual(cls, *args, **kwargs)
        
    def barplot(self, *args, **kwargs):
        """Render a bar plot (histogram).
        
        Arguments:
        
          * values: a 1D vector of bar plot values, or a 2D array where each
            row is an independent bar plot.
          * offset: a 2D vector where offset[i,:] contains the x, y coordinates
            of bar plot #i.
        
        """
        self.add_visual(vs.BarVisual, *args, **kwargs)
        
    def text(self, *args, **kwargs):
        """Render text.
        
        Arguments:
        
          * text: a string or a list of strings
          * coordinates: a tuple with x, y coordinates of the text, or a list 
            with coordinates for each string.
          * fontsize=24: the font size
          * color: the color of the text
          * letter_spacing: the letter spacing
          * interline=0.: the interline when there are several independent 
            texts
        
        """
        self.add_visual(vs.TextVisual, *args, **kwargs)
        
    def rectangles(self, *args, **kwargs):
        """Render one or multiple rectangles.
        
        Arguments:
        
          * coordinates: a 4-tuple with (x0, y0, x1, y1) coordinates, or a list
            of such coordinates for rendering multiple rectangles.
          * color: color(s) of the rectangle(s).
        
        """
        self.add_visual(vs.RectanglesVisual, *args, **kwargs)
    
    def sprites(self, *args, **kwargs):
        """"""
        self.add_visual(vs.SpriteVisual, *args, **kwargs)
       
    def imshow(self, *args, **kwargs):
        """Draw an image.
        
        Arguments:
        
          * texture: a NxMx3 or NxMx4 array with RGB(A) components.
          * points: a 4-tuple with (x0, y0, x1, y1) coordinates of the texture.
          * filter=False: if True, linear filtering and mimapping is used
            if supported by the OpenGL implementation.
        
        """
        filter = kwargs.pop('filter', None)
        if filter:
            kwargs.update(
                mipmap=True,
                minfilter='LINEAR_MIPMAP_NEAREST',
                magfilter='LINEAR',)
        self.add_visual(vs.TextureVisual, *args, **kwargs)
        
    def graph(self, *args, **kwargs):
        """Draw a graph.
        
        Arguments:
        
          * position: a Nx2 array with the coordinates of all nodes.
          * edges: a Nx2-long vector where each row is an edge with the
            nodes indices (integers).
          * color: the color of all nodes, or an array where each row is a 
            node's color.
          * edges_color: the color of all edges, or an array where each row is
            an edge's color.
          * node_size: the node size for all nodes.
        
        """
        
        self.add_visual(vs.GraphVisual, *args, **kwargs)
        
    def mesh(self, *args, **kwargs):
        """Draw a 3D mesh.
        
        Arguments:
        
          * position: the positions as 3D vertices,
          * normal: the normals as 3D vectors,
          * color: the color of each vertex, as 4D vertices.
          * camera_angle: the view angle of the camera, in radians.
          * camera_ratio: the W/H ratio of the camera.
          * camera_zrange: a pair with the far and near z values for the camera
            projection.
        
        """
        self.pmclass = mgs.MeshPaintManager
        self.imclass = mgs.MeshInteractionManager
        self.antialiasing = True
        self.bindingsclass = mgs.MeshBindings
        self.add_visual(vs.MeshVisual, *args, **kwargs)
    
    def surface(self, Z, *args, **kwargs):
        self.pmclass = mgs.MeshPaintManager
        self.imclass = mgs.MeshInteractionManager
        self.antialiasing = True
        self.bindingsclass = mgs.MeshBindings
        self.add_visual(vs.SurfaceVisual, Z, *args, **kwargs)
        
    
    def visual(self, visualcls, *args, **kwargs):
        """Render a custom visual.
        
        Arguments:
        
          * visual_class: the Visual class.
          * *args, **kwargs: the arguments to `visual_class.initialize`.
        
        """
        self.add_visual(visualcls, *args, **kwargs)
    
    def grid(self, *args, **kwargs):
        """Activate the grid."""
        self.show_grid = True
        
        
    # Public interaction methods
    # --------------------------
    def event(self, event, method):
        """Connect an event to a callback method."""
        # self.add_handler(event, method)
        self.handlers[event] = method
        
    def action(self, action, event, *args, **kwargs):
        """Connect an action to an event or a callback method."""
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
        """Connect a callback method to the Animate event.
        
        Arguments:
        
          * method: the callback method,
          * dt: the time step in seconds.
        
        """
        if dt is None:
            dt = .02
        self.animation_interval = dt
        self.event('Animate', method)

    
    # Frame buffer methods
    # --------------------
    def framebuffer(self, *args, **kwargs):
        if 'framebuffer' not in kwargs:
            kwargs['framebuffer'] = 'screen'
        if 'name' not in kwargs:
            kwargs['name'] = 'framebuffer'
        self.visual(vs.FrameBufferVisual, *args, **kwargs)

        
    # Rendering methods
    # -----------------
    def show(self, position=(20,20) ):
        """Show the figure."""
        # self.update_normalization()
        pm = PaintManagerCreator.create(self, self.pmclass)
        im = InteractionManagerCreator.create(self, self.imclass)
        bindings = BindingCreator.create(self, self.bindingsclass)
        window = show_basic_window(
            figure=self,
            paint_manager=pm,
            interaction_manager=im,
            bindings=bindings,
            constrain_ratio=self.constrain_ratio,
            constrain_navigation=self.constrain_navigation,
            display_fps=self.display_fps,
            activate3D=self.activate3D,
            antialiasing=self.antialiasing,
            activate_grid=self.activate_grid,
            momentum=self.momentum,
            show_grid=self.show_grid,
            activate_help=self.activate_help,
            animation_interval=self.animation_interval,
            size=self.figsize,
            position=position,
            toolbar=self.toolbar,
            autosave=self.autosave,
            autodestruct=self.autodestruct,
            )
        return window


# Public figure methods
# ---------------------
def figure(*args, **kwargs):
    """Create a new figure.
    
    Arguments:
    
      * constrain_ratio: constrain the W/H ratio when zooming and resizing
        the window.
      * constrain_navigation: prevent zooming outside the scene.
      * display_fps: display frames per second or not.
      * antialiasing: activate antialiasing or not.
      * size: figure size.
      * toolbar: show the toolbar by default or not.
      
    """
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
    
def surface(*args, **kwargs):
    fig = get_current_figure()
    fig.surface(*args, **kwargs)
    
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


# Frame buffer
# ------------
def framebuffer(*args, **kwargs):
    fig = get_current_figure()
    fig.framebuffer(*args, **kwargs)
    
    

def show(*args, **kwargs):
    fig = get_current_figure()
    fig.show(*args, **kwargs)



    