import numpy as np
from tools import log_debug, log_info, log_warn
from glrenderer import GLRenderer

__all__ = ['PaintManager']


# PaintManager class
# ------------------                   
class PaintManager(object):
    """Defines what to render in the widget."""
    
    # Background color.
    bgcolor = (0., 0., 0., 0.)
    
    # Color of the zoombox rectangle.
    navigation_rectangle_color = (1., 1., 1., .25)
    
    
    # Initialization methods
    # ----------------------
    def __init__(self):
        self.reset()
        # initialize the paint manager (scene and visual creation happens here)
        self.initialize()
        # create the renderer
        self.renderer = GLRenderer(self.scene)
        
    def reset(self):
        # create an empty scene
        self.scene = {'visuals': [], 'renderer_options': {}}
        
    def set_rendering_options(self, **kwargs):
        self.scene['renderer_options'].update(**kwargs)
        
    def initialize(self):
        """Define the scene. To be overriden."""
        
        
    # Visual methods
    # --------------
    def get_visuals(self):
        """Return all visuals defined in the scene."""
        return self.scene['visuals']
        
    def get_visual(self, name):
        visuals = [v for v in self.get_visuals() if v.get('name', '') == name]
        if not visuals:
            return None
        return visuals[0]
        
    
    # Navigation rectangle methods
    # ----------------------------
    def show_navigation_rectangle(self, coordinates):
        """Show the navigation rectangle with the specified coordinates 
        (in relative window coordinates)."""
        # TODO
        # self.set_data(coordinates=coordinates, visible=True,
                      # visual='navigation_rectangle')
            
    def hide_navigation_rectangle(self):
        """Hide the navigation rectangle."""
        # TODO
        # self.set_data(visible=False, visual='navigation_rectangle')
        
        
    # Data creation methods
    # ---------------------
    def add_visual(self, visual_class, *args, **kwargs):
        """Add a visual. This method should be called in `self.initialize`.
        
        A visual is an instanciation of a `DataVisual`. A DataVisual
        defines a pattern for one, or a homogeneous set of plotting objects.
        Example: a text string, a set of rectangles, a set of triangles,
        a set of curves, a set of points. A set of points and rectangles
        does not define a visual since it is not an homogeneous set of
        objects. The technical reason for this distinction is that OpenGL
        allows for very fast rendering of homogeneous objects by calling
        a single rendering command (even if several objects of the same type
        need to be rendered, e.g. several rectangles). The lower the number
        of rendering calls, the better the performance.
        
        Hence, a visual is defined by a particular DataVisual, and by
        specification of fields in this visual (positions of the points,
        colors, text string for the example of the TextVisual, etc.). It
        also comes with a number `N` which is the number of vertices contained
        in the visual (N=4 for one rectangle, N=len(text) for a text since 
        every character is rendered independently, etc.)
        
        Several visuals can be created in the PaintManager, but performance
        decreases with the number of visuals, so that all homogeneous 
        objects to be rendered on the screen at the same time should be
        grouped into a single visual (e.g. multiple line plots).
        
        Arguments:
          * visual_class=None: the visual class, deriving from
            `Visual` (or directly from the base class `DataVisual`
            if you don't want the navigation-related functionality).
          * visible=True: whether this visual should be rendered. Useful
            for showing/hiding a transient element. When hidden, the visual
            does not go through the rendering pipeline at all.
          
        Returns:
          * visual: a dictionary containing all the information about
            the visual, and that can be used in `set_data`.
        
        """
        # get the name of the visual from kwargs
        name = kwargs.pop('name', 'visual')
        if self.get_visual(name):
            raise ValueError("Visual name '%s' already exists." % name)
        # create the visual object
        visual = visual_class(*args, **kwargs)
        # get the dictionary version
        dic = visual.get_dic()
        dic['name'] = name
        # append the dic to the visuals list of the scene
        self.get_visuals().append(dic)
        
    def set_data(self, visual=None, **kwargs):
        """Specify or change the data associated to particular visual
        fields.
        
        Actual data upload on the GPU will occur during the rendering process, 
        in `paintGL`. It is just recorded here for later use.
        
        Arguments:
          * visual=None: the relevant visual. By default, the first one
            that has been created in `initialize`.
          * **kwargs: keyword arguments as `visual_field_name: value` pairs.
        
        """
        # default name
        if visual is None:
            visual = 'visual'
        self.renderer.set_data(visual, **kwargs)
            
            
    # Methods related to visuals
    # --------------------------
    def transform_view(self):
        """Change uniform variables to implement interactive navigation."""
        # TODO: modularize this
        tx, ty = self.interaction_manager.get_translation()
        sx, sy = self.interaction_manager.get_scaling()
        # scale = (np.float32(sx), np.float32(sy))
        scale = (sx, sy)
        # translation = (np.float32(tx), np.float32(ty))
        translation = (tx, ty)
        # update all non static visuals
        for visual in self.get_visuals():
            if not visual.get('is_static', False):
                self.set_data(visual=visual['name'], 
                              scale=scale, translation=translation)
    
    def update_fps(self, fps):
        """Update the FPS in the corresponding text visual."""
        self.set_data(visual='fps', text="FPS: %03d" % fps)
 
 
    # Rendering methods
    # -----------------
    def initializeGL(self):
        self.renderer.initialize()
 
    def paintGL(self):
        self.transform_view()
        self.renderer.paint()
 
    def resizeGL(self, width, height):
        self.renderer.resize(width, height)
        
    def updateGL(self):
        """Call updateGL in the parent widget."""
        self.parent.updateGL()
        
        
    # Cleanup methods
    # ---------------
    def cleanup(self):
        """Cleanup all visuals."""
        self.renderer.cleanup()
        
        
    # Methods to be overriden
    # -----------------------
    def initialize(self):
        """Initialize the data. To be overriden.

        This method can make calls to `add_visual` and `set_data` methods.
        
        """
        pass
