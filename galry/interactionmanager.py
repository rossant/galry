import numpy as np
import OpenGL.GL as gl
import OpenGL.GLU as glu
from interactionevents import InteractionEvents
from tools import extend_enum
import cursors

__all__ = ['InteractionManager']

class InteractionManager(object):
    """This class implements the processing of the raised interaction events.
    
    To be overriden.
    
    """
    # current cursor and base cursor for the active interaction mode
    cursor = None
    base_cursor = None
    
    # zoom box
    navigation_rectangle = None
    constrain_navigation = True
    
    def __init__(self):
        # initialize navigation
        self.reset()
        self.set_navigation_constraints()
        self.activate_navigation_constrain()
        self.initialize()
        
    def initialize(self):
        """Initialize the InteractionManager.
        
        To be overriden.
        """
        pass
        
    def extend_events(self, custom_events=None):
        if custom_events:
            self.events = extend_enum(InteractionEvents, custom_events)
        else:
            self.events = InteractionEvents
    
    # Event processing methods
    # ------------------------
    def process_none_event(self):
        # when zoombox event finished: set_relative_viewbox
        if (self.navigation_rectangle is not None):
            self.set_relative_viewbox(*self.navigation_rectangle)
        self.navigation_rectangle = None
        self.cursor = None
    
    def process_navigation_event(self, event, parameter):
        # if "cursors" not in globals():
            # import cursors
        if event == self.events.PanEvent:
            self.pan(parameter)
            self.cursor = cursors.ClosedHandCursor
    
    def process_zoom_event(self, event, parameter):
        # if "cursors" not in globals():
            # import cursors
        if event == self.events.ZoomEvent:
            self.zoom(parameter)
            self.cursor = cursors.MagnifyingGlassCursor
        if event == self.events.ZoomBoxEvent:
            self.zoombox(parameter)
            self.cursor = cursors.MagnifyingGlassCursor
    
    def process_reset_event(self, event, parameter):
        if event == self.events.ResetEvent:
            self.reset()
            self.cursor = None
        if event == self.events.ResetZoomEvent:
            self.reset_zoom()
            self.cursor = None
        
    def process_event(self, event, parameter):
        """Process an event.
        
        This is the main method of this class. It is called as soon as an 
        interaction event is raised by an user action.
        
        Arguments:
          * event: the event to process, an InteractionEvent enum value.
          * parameter: the parameter returned by the param_getter function
            specified in the related binding.
        
        """
        # HACK: a QApplication needs to be constructed for creating Pixmap
        # cursors, so we load (and create the cursors) here
        if event is None:
            self.process_none_event()
        self.process_navigation_event(event, parameter)
        self.process_zoom_event(event, parameter)
        self.process_reset_event(event, parameter)
        self.process_extended_event(event, parameter)
        
    def process_extended_event(self, event, parameter):
        pass
            
    # Navigation methods
    # ------------------    
    def set_navigation_constraints(self, constraints=None):
        """Set the navigation constraints.
        
        Arguments:
          * constraints=None: the coordinates of the bounding box as 
            (xmin, ymin, xmax, ymax), by default (+-1).
        
        """
        if not constraints:
            constraints = (-1, -1, 1, 1)
        # view constraints
        self.xmin, self.ymin, self.xmax, self.ymax = constraints
        # minimum zoom allowed
        self.sxmin = 1./min(self.xmax, -self.xmin)
        self.symin = 1./min(self.ymax, -self.ymin)
        # maximum zoom allowed
        self.sxmax = self.symax = 1e6
        
    def reset(self):
        """Reset the navigation."""
        self.tx, self.ty = 0, 0
        self.sx, self.sy = 1, 1
        self.sxl, self.syl = 1, 1
        self.navigation_rectangle = None
    
    def pan(self, parameter):
        """Pan along the x,y coordinates.
        
        Arguments:
          * parameter: (dx, dy)
        
        """
        self.tx += parameter[0] / self.sx
        self.ty += parameter[1] / self.sy
    
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
        self.tx += -px * (1./self.sxl - 1./self.sx)
        self.sxl = self.sx
        self.sy *= np.exp(dy)
        self.ty += -py * (1./self.syl - 1./self.sy)
        self.syl = self.sy
    
    def zoombox(self, parameter):
        """Indicate to draw a zoom box.
        
        Arguments:
          * parameter: the box coordinates (xmin, ymin, xmax, ymax)
        
        """
        # do nothing if the box is too small
        if ((np.abs(parameter[2] - parameter[0]) > .05) and \
             np.abs(parameter[3] - parameter[1]) > .05):
            self.navigation_rectangle = parameter
            self.paint_manager.add_transient_overlay("rectangle", self.navigation_rectangle, 
                        (.5, .5, .5, .5))
        else:
            self.navigation_rectangle = None
    
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
    
    def get_scaling(self):
        """Return the scaling vector.
        
        Returns:
          * sx, sy: scaling coordinates.
        
        """
        if self.constrain_navigation:
            self.activate_navigation_constrain()
        return self.sx, self.sy

    def get_cursor(self):
        """Return the current cursor."""
        if self.cursor is None:
            return self.base_cursor
        else:
            return self.cursor
          