from galry import NavigationEventProcessor, InteractionManager, QtCore, \
    PaintManager, \
    GridEventProcessor, scale_matrix, rotation_matrix, translation_matrix, \
    MeshNavigationEventProcessor
from plot_manager import PlotBindings
    
import OpenGL.GL as gl
import numpy as np

         
class MeshInteractionManager(InteractionManager):
    def initialize_default(self, constrain_navigation=None):
        super(MeshInteractionManager, self).initialize_default()
        self.add_processor(MeshNavigationEventProcessor, name='navigation')
        self.add_processor(GridEventProcessor, name='grid')
        
        
class MeshPaintManager(PaintManager):
    def initialize_default(self, *args, **kwargs):
        self.set_rendering_options(activate3D=True)
        
        
class MeshBindings(PlotBindings):
    def initialize(self):
        super(MeshBindings, self).initialize()
        self.set_rotation_mouse()
        self.set_rotation_keyboard()
    
    def set_panning_mouse(self):
        # Panning: CTRL + left button mouse
        self.set('LeftClickMove', 'Pan',
                    # key_modifier='Control',
                    param_getter=lambda p: (-4*p["mouse_position_diff"][0],
                                            -4*p["mouse_position_diff"][1]))
        
    def set_rotation_mouse(self):
        # Rotation: left button mouse
        self.set('MiddleClickMove', 'Rotation',
                    param_getter=lambda p: (3*p["mouse_position_diff"][0],
                                            3*p["mouse_position_diff"][1]))    
             
    def set_rotation_keyboard(self):
        """Set zooming bindings with the keyboard."""
        # Rotation: ALT + key arrows
        self.set('KeyPress', 'Rotation',
                    key='Left', key_modifier='Shift', 
                    param_getter=lambda p: (-.25, 0))
        self.set('KeyPress', 'Rotation',
                    key='Right', key_modifier='Shift', 
                    param_getter=lambda p: (.25, 0))
        self.set('KeyPress', 'Rotation',
                    key='Up', key_modifier='Shift', 
                    param_getter=lambda p: (0, .25))
        self.set('KeyPress', 'Rotation',
                    key='Down', key_modifier='Shift', 
                    param_getter=lambda p: (0, -.25))
                    
    def set_zoombox_mouse(self):
        """Deactivate zoombox."""
        pass

    def set_zoombox_keyboard(self):
        """Deactivate zoombox."""
        pass
    
    def extend(self):
        """Set rotation interactions with mouse and keyboard."""
        self.set_rotation_mouse()
        self.set_rotation_keyboard()
        
        