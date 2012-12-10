import numpy as np
import cursors
from manager import Manager
# from interactionevents import InteractionEvents as events

__all__ = ['InteractionManager']

# Maximum viewbox allowed when constraining navigation.
MAX_VIEWBOX = (-1., -1., 1., 1.)

class InteractionManager(Manager):
    """This class implements the processing of the raised interaction events.
    
    To be overriden.
    
    """
    # current cursor and base cursor for the active interaction mode
    cursor = None
    base_cursor = None
    
    # zoom box
    navigation_rectangle = None
    constrain_navigation = False
    
    def __init__(self, parent):
        # self.parent = parent
        # initialize navigation
        # self.reset()
        super(InteractionManager, self).__init__(parent)
        self.set_navigation_constraints()
        self.activate_navigation_constrain()
        self.initialize()
        
    def initialize(self):
        """Initialize the InteractionManager.
        
        To be overriden.
        """
        pass
        
        
    # Event processing methods
    # ------------------------
    def process_none_event(self):
        """Process the None event, i.e. where there is no event. Useful
        to trigger an action at the end of a long-lasting event."""
        # when zoombox event finished: set_relative_viewbox
        if (self.navigation_rectangle is not None):
            self.set_relative_viewbox(*self.navigation_rectangle)
            self.paint_manager.hide_navigation_rectangle()
        self.navigation_rectangle = None
        self.cursor = None
    
    def process_pan_event(self, event, parameter):
        """Process a pan-related event."""
        if event == 'PanEvent':
            self.pan(parameter)
            self.cursor = cursors.ClosedHandCursor
    
    def process_rotation_event(self, event, parameter):
        if event == 'RotationEvent':
            self.rotate(parameter)
            self.cursor = cursors.ClosedHandCursor

    def process_zoom_event(self, event, parameter):
        """Process a zoom-related event."""
        if event == 'ZoomEvent':
            self.zoom(parameter)
            self.cursor = cursors.MagnifyingGlassCursor
        if event == 'ZoomBoxEvent':
            self.zoombox(parameter)
            self.cursor = cursors.MagnifyingGlassCursor
    
    def process_reset_event(self, event, parameter):
        """Process a reset-related event."""
        if event == 'ResetEvent':
            self.reset()
            self.cursor = None
        if event == 'ResetZoomEvent':
            self.reset_zoom()
            self.cursor = None
        
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
        if event is None:
            self.process_none_event()
        self.process_fullscreen_event(event, parameter)
        self.process_pan_event(event, parameter)
        self.process_rotation_event(event, parameter)
        self.process_zoom_event(event, parameter)
        self.process_reset_event(event, parameter)
        self.process_custom_event(event, parameter)
        
    def process_custom_event(self, event, parameter):
        """Process a custom event."""
        pass
           
           
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

    def get_cursor(self):
        """Return the current cursor."""
        if self.cursor is None:
            return self.base_cursor
        else:
            return self.cursor
          