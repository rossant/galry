import inspect
import time
import numpy as np
from processor import EventProcessor
from galry import Manager, TextVisual, get_color


__all__ = ['NavigationEventProcessor']

      
# Maximum viewbox allowed when constraining navigation.
MAX_VIEWBOX = (-1., -1., 1., 1.)

class NavigationEventProcessor(EventProcessor):
    """Handle navigation-related events."""
    def initialize(self, constrain_navigation=False,
        normalization_viewbox=None, momentum=False):
        # zoom box
        self.navigation_rectangle = None
        self.constrain_navigation = constrain_navigation
        self.normalization_viewbox = normalization_viewbox
        
        self.reset()
        self.set_navigation_constraints()
        self.activate_navigation_constrain()
        
        # register events processors
        self.register('Pan', self.process_pan_event)
        self.register('Rotation', self.process_rotation_event)
        self.register('Zoom', self.process_zoom_event)
        self.register('ZoomBox', self.process_zoombox_event)
        self.register('Reset', self.process_reset_event)
        self.register('ResetZoom', self.process_resetzoom_event)
        self.register('SetPosition', self.process_setposition_event)
        self.register('SetViewbox', self.process_setviewbox_event)
        
        # Momentum
        if momentum:
            self.register('Animate', self.process_animate_event)
            
        self.pan_list = []
        self.pan_list_maxsize = 10
        self.pan_vec = np.zeros(2)
        self.is_panning = False
        self.momentum = False
        
        self.register('Grid', self.process_grid_event)
        self.grid_visible = getattr(self.parent, 'show_grid', False)
        self.activate_grid()
        
    def activate_grid(self):
        self.set_data(visual='grid_lines', visible=self.grid_visible)
        self.set_data(visual='grid_text', visible=self.grid_visible)
        processor = self.get_processor('grid')
        # print processor
        if processor:
            processor.activate(self.grid_visible)
            if self.grid_visible:
                processor.update_axes(None)
        
    def process_grid_event(self, parameter):
        self.grid_visible = not(self.grid_visible)
        self.activate_grid()
        
    def transform_view(self):
        """Change uniform variables to implement interactive navigation."""
        translation = self.get_translation()
        scale = self.get_scaling()
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
        # Trigger panning momentum
        if self.is_panning:
            self.is_panning = False
            if len(self.pan_list) >= self.pan_list_maxsize:
                self.momentum = True
        self.parent.block_refresh = False
        # self.set_cursor(None)
        self.transform_view()

    def add_pan(self, parameter):
        # Momentum.
        self.pan_list.append(parameter)
        if len(self.pan_list) > self.pan_list_maxsize:
            del self.pan_list[0]
        self.pan_vec = np.array(self.pan_list).mean(axis=0)
        
    def process_pan_event(self, parameter):
        # Momentum.
        self.is_panning = True
        self.momentum = False
        self.parent.block_refresh = False
        self.add_pan(parameter)
        
        self.pan(parameter)
        self.set_cursor('ClosedHandCursor')
        self.transform_view()

    def process_animate_event(self, parameter):
        # Momentum.
        if self.is_panning:
            self.add_pan((0., 0.))
        if self.momentum:
            self.pan(self.pan_vec)
            self.pan_vec *= .975
            # End momentum.
            if (np.abs(self.pan_vec) < .0001).all():
                self.momentum = False
                self.parent.block_refresh = True
                self.pan_list = []
                self.pan_vec = np.zeros(2)
            self.transform_view()
    
    def process_rotation_event(self, parameter):
        self.rotate(parameter)
        self.set_cursor('ClosedHandCursor')
        self.transform_view()

    def process_zoom_event(self, parameter):
        self.zoom(parameter)
        self.parent.block_refresh = False
        # Block momentum when zooming.
        self.momentum = False
        self.set_cursor('MagnifyingGlassCursor')
        self.transform_view()
        
    def process_zoombox_event(self, parameter):
        self.zoombox(parameter)
        self.parent.block_refresh = False
        self.set_cursor('MagnifyingGlassCursor')
        self.transform_view()
    
    def process_reset_event(self, parameter):
        self.reset()
        self.parent.block_refresh = False
        self.set_cursor(None)
        self.transform_view()

    def process_resetzoom_event(self, parameter):
        self.reset_zoom()
        self.parent.block_refresh = False
        self.set_cursor(None)
        self.transform_view()
        
    def process_setposition_event(self, parameter):
        self.set_position(*parameter)
        self.parent.block_refresh = False
        self.transform_view()
        
    def process_setviewbox_event(self, parameter):
        self.set_viewbox(*parameter)
        self.parent.block_refresh = False
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
    
    def get_viewbox(self, scale=1.):
        """Return the coordinates of the current view box.
        
        Returns:
          * (xmin, ymin, xmax, ymax): the current view box in data coordinate
            system.
            
        """
        x0, y0 = self.get_data_coordinates(-scale, -scale)
        x1, y1 = self.get_data_coordinates(scale, scale)
        return (x0, y0, x1, y1)
    
    def get_data_coordinates(self, x, y):
        """Convert window relative coordinates into data coordinates.
        
        Arguments:
          * x, y: coordinates in [-1, 1] of a point in the window.
          
        Returns:
          * x', y': coordinates of this point in the data coordinate system.
        
        """
        return x/self.sx - self.tx, y/self.sy - self.ty
        
    def get_window_coordinates(self, x, y):
        """Inverse of get_data_coordinates.
        """
        return (x + self.tx) * self.sx, (y + self.ty) * self.sy
    
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
        # prevent too small zoombox
        if (np.abs(x1 - x0) < .07) & (np.abs(y1 - y0) < .07):
            return
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
        if self.constrain_navigation:
            # constrain scaling
            self.sx = np.clip(self.sx, self.sxmin, self.sxmax)
            self.sy = np.clip(self.sy, self.symin, self.symax)
            # constrain translation
            self.tx = np.clip(self.tx, 1./self.sx - self.xmax,
                                      -1./self.sx - self.xmin)
            self.ty = np.clip(self.ty, 1./self.sy + self.ymin,
                                      -1./self.sy + self.ymax)
        else:
            # constrain maximum zoom anyway
            self.sx = min(self.sx, self.sxmax)
            self.sy = min(self.sy, self.symax)
    
    def get_translation(self):
        """Return the translation vector.
        
        Returns:
          * tx, ty: translation coordinates.
        
        """
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

 
