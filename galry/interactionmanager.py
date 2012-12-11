import numpy as np
import inspect
# import cursors
from manager import Manager


__all__ = ['InteractionManager', 'EventProcessor', 'NavigationEventProcessor']


class EventProcessor(object):
    """Process several related events."""
    def __init__(self, interaction_manager, *args, **kwargs):
        self.interaction_manager = interaction_manager
        self.parent = interaction_manager.parent
        self.handlers = {}
        
        # current cursor and base cursor for the active interaction mode
        self.cursor = None
        # self.base_cursor = None
        
        self.initialize(*args, **kwargs)
        
    def get_processor(self, name):
        return self.interaction_manager.get_processor(name)
        
    def _get_paint_manager(self):
        return self.interaction_manager.paint_manager
    paint_manager = property(_get_paint_manager)
        
    def set_data(self, *args, **kwargs):
        # shortcut to paint_manager.set_data
        return self.interaction_manager.paint_manager.set_data(*args, **kwargs)
        
    def set_cursor(self, cursor):
        self.cursor = cursor
        
    def get_cursor(self):
        """Return the current cursor."""
        # if self.cursor is None:
            # return self.base_cursor
        # else:
        return self.cursor
        
    def register(self, event, method):
        """Register a handler for the event."""
        self.handlers[event] = method
        
    def registered(self, event):
        """Return whether the specified event has been registered by this
        processor."""
        return self.handlers.get(event, None) is not None
        
        
    # Methods to override
    # -------------------
    def initialize(self, *args, **kwargs):
        """Initialize the event processor by calling self.register to register
        handlers for different events."""
        pass
        
    def process(self, event, parameter):
        """Process an event by calling the registered handler if there's one.
        """
        method = self.handlers.get(event, None)
        if method:
            # if the method is a method of a class deriving from EventProcessor
            # we pass just parameter
            if inspect.ismethod(method) and EventProcessor in inspect.getmro(method.im_class):
                method(parameter)
            else:
                # here, we are using the high level interface and figure
                # is the Figure object we pass to this function
                method(self.interaction_manager.figure, parameter)

    def process_none(self):
        """Process the None event, occuring when there's no event, or when
        an event has just finished."""
        pass
        
      
# Maximum viewbox allowed when constraining navigation.
MAX_VIEWBOX = (-1., -1., 1., 1.)

class NavigationEventProcessor(EventProcessor):
    """Handle navigation-related events."""
    def initialize(self, constrain_navigation=False):
        # zoom box
        self.navigation_rectangle = None
        self.constrain_navigation = constrain_navigation
        
        self.reset()
        self.set_navigation_constraints()
        self.activate_navigation_constrain()
        
        # register events processors
        self.register('PanEvent', self.process_pan_event)
        self.register('RotationEvent', self.process_rotation_event)
        self.register('ZoomEvent', self.process_zoom_event)
        self.register('ZoomBoxEvent', self.process_zoombox_event)
        self.register('ResetEvent', self.process_reset_event)
        self.register('ResetZoomEvent', self.process_resetzoom_event)
        
    def transform_view(self):
        """Change uniform variables to implement interactive navigation."""
        tx, ty = self.get_translation()
        sx, sy = self.get_scaling()
        # scale = (np.float32(sx), np.float32(sy))
        scale = (sx, sy)
        # translation = (np.float32(tx), np.float32(ty))
        translation = (tx, ty)
        # update all non static visuals
        for visual in self.paint_manager.get_visuals():
            if not visual.get('is_static', False):
                self.set_data(visual=visual['name'], 
                              scale=scale, translation=translation)
        
        
    # Event processing methods
    # ------------------------
    def process_none(self):
        """Process the None event, i.e. where there is no event. Useful
        to trigger an action at the end of a long-lasting event."""
        # when zoombox event finished: set_relative_viewbox
        if (self.navigation_rectangle is not None):
            self.set_relative_viewbox(*self.navigation_rectangle)
            self.paint_manager.hide_navigation_rectangle()
        self.navigation_rectangle = None
        # self.set_cursor(None)
        self.transform_view()

    def process_pan_event(self, parameter):
        self.pan(parameter)
        self.set_cursor('ClosedHandCursor')
        self.transform_view()
    
    def process_rotation_event(self, parameter):
        self.rotate(parameter)
        self.set_cursor('ClosedHandCursor')
        self.transform_view()

    def process_zoom_event(self, parameter):
        self.zoom(parameter)
        self.set_cursor('MagnifyingGlassCursor')
        self.transform_view()
        
    def process_zoombox_event(self, parameter):
        self.zoombox(parameter)
        self.set_cursor('MagnifyingGlassCursor')
        self.transform_view()
    
    def process_reset_event(self, parameter):
        self.reset()
        self.set_cursor(None)
        self.transform_view()

    def process_resetzoom_event(self, parameter):
        self.reset_zoom()
        self.set_cursor(None)
        self.transform_view()
        
        
    # Navigation methods
    # ------------------    
    def set_navigation_constraints(self, constraints=None, maxzoom=1e6):
        """Set the navigation constraints.
        
        Arguments:
          * constraints=None: the coordinates of the bounding box as 
            (xmin, ymin, xmax, ymax), by default (+-1).
        
        """
        if not constraints:
            constraints = MAX_VIEWBOX
        # view constraints
        self.xmin, self.ymin, self.xmax, self.ymax = constraints
        # minimum zoom allowed
        self.sxmin = 1./min(self.xmax, -self.xmin)
        self.symin = 1./min(self.ymax, -self.ymin)
        # maximum zoom allowed
        self.sxmax = self.symax = maxzoom
        
    def reset(self):
        """Reset the navigation."""
        self.tx, self.ty, self.tz = 0., 0., 0.
        self.sx, self.sy = 1., 1.
        self.sxl, self.syl = 1., 1.
        self.rx, self.ry = 0., 0.
        self.navigation_rectangle = None
    
    def pan(self, parameter):
        """Pan along the x,y coordinates.
        
        Arguments:
          * parameter: (dx, dy)
        
        """
        self.tx += parameter[0] / self.sx
        self.ty += parameter[1] / self.sy
    
    def rotate(self, parameter):
        self.rx += parameter[0]
        self.ry += parameter[1]
    
    def zoom(self, parameter):
        """Zoom along the x,y coordinates.
        
        Arguments:
          * parameter: (dx, px, dy, py)
        
        """
        dx, px, dy, py = parameter
        if self.parent.constrain_ratio:
            if (dx >= 0) and (dy >= 0):
                dx, dy = (max(dx, dy),) * 2
            elif (dx <= 0) and (dy <= 0):
                dx, dy = (min(dx, dy),) * 2
            else:
                dx = dy = 0
        self.sx *= np.exp(dx)
        self.sy *= np.exp(dy)
        
        # constrain scaling
        if self.constrain_navigation:
            self.sx = np.clip(self.sx, self.sxmin, self.sxmax)
            self.sy = np.clip(self.sy, self.symin, self.symax)
        
        self.tx += -px * (1./self.sxl - 1./self.sx)
        self.ty += -py * (1./self.syl - 1./self.sy)
        self.sxl = self.sx
        self.syl = self.sy
    
    def zoombox(self, parameter):
        """Indicate to draw a zoom box.
        
        Arguments:
          * parameter: the box coordinates (xmin, ymin, xmax, ymax)
        
        """
        self.navigation_rectangle = parameter
        self.paint_manager.show_navigation_rectangle(parameter)
    
    def reset_zoom(self):
        """Reset the zoom."""
        self.sx, self.sy = 1, 1
        self.sxl, self.syl = 1, 1
        self.navigation_rectangle = None
    
    def get_viewbox(self):
        """Return the coordinates of the current view box.
        
        Returns:
          * (xmin, ymin, xmax, ymax): the current view box in data coordinate
            system.
            
        """
        x0, y0 = self.get_data_coordinates(-1, -1)
        x1, y1 = self.get_data_coordinates(1, 1)
        return (x0, y0, x1, y1)
    
    def get_data_coordinates(self, x, y):
        """Convert window relative coordinates into data coordinates.
        
        Arguments:
          * x, y: coordinates in [-1, 1] of a point in the window.
          
        Returns:
          * x', y': coordinates of this point in the data coordinate system.
        
        """
        return x/self.sx - self.tx, y/self.sy - self.ty
    
    def constrain_viewbox(self, x0, y0, x1, y1):
        """Constrain the viewbox ratio."""
        if (x1-x0) > (y1-y0):
            d = ((x1-x0)-(y1-y0))/2
            y0 -= d
            y1 += d
        else:
            d = ((y1-y0)-(x1-x0))/2
            x0 -= d
            x1 += d
        return x0, y0, x1, y1
    
    def set_viewbox(self, x0, y0, x1, y1):
        """Set the view box in the data coordinate system.
        
        Arguments:
          * x0, y0, x1, y1: viewbox coordinates in the data coordinate system.
        
        """
        # force the zoombox to keep its original ratio
        if self.parent.constrain_ratio:
            x0, y0, x1, y1 = self.constrain_viewbox(x0, y0, x1, y1)
        if (x1-x0) and (y1-y0):
            self.tx = -(x1+x0)/2
            self.ty = -(y1+y0)/2
            self.sx = 2./abs(x1-x0)
            self.sy = 2./abs(y1-y0)
            self.sxl, self.syl = self.sx, self.sy
    
    def set_relative_viewbox(self, x0, y0, x1, y1):
        """Set the view box in the window coordinate system.
        
        Arguments:
          * x0, y0, x1, y1: viewbox coordinates in the window coordinate system.
            These coordinates are all in [-1, 1].
        
        """
        # force the zoombox to keep its original ratio
        if self.parent.constrain_ratio:
            x0, y0, x1, y1 = self.constrain_viewbox(x0, y0, x1, y1)
        if (x1-x0) and (y1-y0):
            self.tx += -(x1+x0)/(2*self.sx)
            self.ty += -(y1+y0)/(2*self.sy)
            self.sx *= 2./abs(x1-x0)
            self.sy *= 2./abs(y1-y0)
            self.sxl, self.syl = self.sx, self.sy
    
    def set_position(self, x, y):
        """Set the current position.
        
        Arguments:
          * x, y: coordinates in the data coordinate system.
        
        """
        self.tx = -x
        self.ty = -y
    
    def activate_navigation_constrain(self):
        """Constrain the navigation to a bounding box."""
        # constrain scaling
        self.sx = np.clip(self.sx, self.sxmin, self.sxmax)
        self.sy = np.clip(self.sy, self.symin, self.symax)
        # constrain translation
        self.tx = np.clip(self.tx, 1./self.sx - self.xmax,
                                  -1./self.sx - self.xmin)
        self.ty = np.clip(self.ty, 1./self.sy + self.ymin,
                                  -1./self.sy + self.ymax)
    
    def get_translation(self):
        """Return the translation vector.
        
        Returns:
          * tx, ty: translation coordinates.
        
        """
        if self.constrain_navigation:
            self.activate_navigation_constrain()
        return self.tx, self.ty
    
    def get_rotation(self):
        return self.rx, self.ry
    
    def get_scaling(self):
        """Return the scaling vector.
        
        Returns:
          * sx, sy: scaling coordinates.
        
        """
        if self.constrain_navigation:
            self.activate_navigation_constrain()
        return self.sx, self.sy

        
class InteractionManager(Manager):
    """This class implements the processing of the raised interaction events.
    
    To be overriden.
    
    """
    
    # Initialization methods
    # ----------------------
    def __init__(self, parent):
        super(InteractionManager, self).__init__(parent)
        self.cursor = None
        self.prev_event = None
        self.processors = {}
        self.initialize_default(
            constrain_navigation=self.parent.constrain_navigation)
        self.initialize()
        
    def initialize(self):
        """Initialize the InteractionManager.
        
        To be overriden.
        """
        pass
        
    def initialize_default(self, constrain_navigation=False):
        self.add_processor(NavigationEventProcessor,
            constrain_navigation=constrain_navigation, name='navigation')
        
        
    # Processor methods
    # -----------------
    def get_processors(self):
        return self.processors
        
    def get_processor(self, name):
        if name is None:
            name = 'processor0'
        return self.processors.get(name, None)
        
    def add_processor(self, cls, *args, **kwargs):
        # get the name of the visual from kwargs
        name = kwargs.pop('name', 'processor%d' % (len(self.get_processors())))
        if self.get_processor(name):
            raise ValueError("Processor name '%s' already exists." % name)
        processor = cls(self, *args, **kwargs)
        self.processors[name] = processor
        return processor
        
    def add_default_processor(self):
        return self.add_processor(EventProcessor, name='default_processor')
        
    def register(self, event, method):
        processor = self.get_processor('default_processor')
        if processor is None:
            processor = self.add_default_processor()
        processor.register(event, method)
        
        
    # Event processing methods
    # ------------------------
    def process_fullscreen_event(self, event, parameter):
        if event == 'ToggleFullScreenEvent':
            self.parent.toggle_fullscreen()
        
    def process_event(self, event, parameter):
        """Process an event.
        
        This is the main method of this class. It is called as soon as an 
        interaction event is raised by an user action.
        
        Arguments:
          * event: the event to process, an InteractionEvent string.
          * parameter: the parameter returned by the param_getter function
            specified in the related binding.
        
        """
        
        # process None events in all processors
        if event is None and self.prev_event is not None:
            for name, processor in self.get_processors().iteritems():
                processor.process_none()
            self.cursor = None
        
        if event == 'ToggleFullScreenEvent':
            self.process_fullscreen_event(event, parameter)
            # toggle_fullscreen
        
        # process events in all processors
        for name, processor in self.get_processors().iteritems():
            if processor.registered(event):
                processor.process(event, parameter)
                self.cursor = processor.get_cursor()
        
        self.prev_event = event
        
    def get_cursor(self):
        return self.cursor
        
        
        
        
        