from galry.processors import NavigationEventProcessor
from galry import PaintManager, InteractionManager, GridEventProcessor, \
    RectanglesVisual, GridVisual, BindingSet


class PlotPaintManager(PaintManager):
    def initialize_default(self):
        super(PlotPaintManager, self).initialize_default()
        # Navigation rectangle
        self.add_visual(RectanglesVisual, coordinates=(0.,) * 4,
                        color=self.navigation_rectangle_color, 
                        is_static=True,
                        name='navigation_rectangle',
                        visible=False)
        
        # Grid
        if self.parent.activate_grid:
            self.add_visual(GridVisual, name='grid', visible=False)


class PlotInteractionManager(InteractionManager):
    def initialize_default(self, constrain_navigation=None):
        super(PlotInteractionManager, self).initialize_default()
        self.add_processor(NavigationEventProcessor,
            constrain_navigation=constrain_navigation, name='navigation')
        self.add_processor(GridEventProcessor, name='grid')
        
        
class PlotBindings(BindingSet):
    """A default set of bindings for interactive navigation.
    
    This binding set makes use of the keyboard and the mouse.
    
    """
    def set_widget(self):
        # self.set('KeyPress', 'ToggleFullscreen', key='F')
        # self.set('KeyPress', 'Help', key='H')
        self.set('KeyPress', 'Grid', key='QuoteDbl')
    
    def set_panning_mouse(self):
        """Set panning bindings with the mouse."""
        # Panning: left button mouse
        self.set('LeftClickMove', 'Pan',
                    param_getter=lambda p: (p["mouse_position_diff"][0],
                                            p["mouse_position_diff"][1]))
        
    def set_panning_keyboard(self):
        """Set panning bindings with the keyboard."""
        # Panning: keyboard arrows
        self.set('KeyPress', 'Pan',
                    key='Left',
                    param_getter=lambda p: (.24, 0))
        self.set('KeyPress', 'Pan',
                    key='Right',
                    param_getter=lambda p: (-.24, 0))
        self.set('KeyPress', 'Pan',
                    key='Up',
                    param_getter=lambda p: (0, -.24))
        self.set('KeyPress', 'Pan',
                    key='Down',
                    param_getter=lambda p: (0, .24))
                
    def set_zooming_mouse(self):
        """Set zooming bindings with the mouse."""
        # Zooming: right button mouse
        self.set('RightClickMove', 'Zoom',
                    param_getter=lambda p: (p["mouse_position_diff"][0]*2.5,
                                            p["mouse_press_position"][0],
                                            p["mouse_position_diff"][1]*2.5,
                                            p["mouse_press_position"][1]))
    
    def set_zoombox_mouse(self):
        """Set zoombox bindings with the mouse."""
        # Zooming: zoombox (drag and drop)
        self.set('MiddleClickMove', 'ZoomBox',
                    param_getter=lambda p: (p["mouse_press_position"][0],
                                            p["mouse_press_position"][1],
                                            p["mouse_position"][0],
                                            p["mouse_position"][1]))
    
    def set_zoombox_keyboard(self):
        """Set zoombox bindings with the keyboard."""
        # Idem but with CTRL + left button mouse 
        self.set('LeftClickMove', 'ZoomBox',
                    key_modifier='Control',
                    param_getter=lambda p: (p["mouse_press_position"][0],
                                            p["mouse_press_position"][1],
                                            p["mouse_position"][0],
                                            p["mouse_position"][1]))
                 
    def set_zooming_keyboard(self):
        """Set zooming bindings with the keyboard."""
        # Zooming: ALT + key arrows
        self.set('KeyPress', 'Zoom',
                    key='Left', key_modifier='Control', 
                    param_getter=lambda p: (-.25, 0, 0, 0))
        self.set('KeyPress', 'Zoom',
                    key='Right', key_modifier='Control', 
                    param_getter=lambda p: (.25, 0, 0, 0))
        self.set('KeyPress', 'Zoom',
                    key='Up', key_modifier='Control', 
                    param_getter=lambda p: (0, 0, .25, 0))
        self.set('KeyPress', 'Zoom',
                    key='Down', key_modifier='Control', 
                    param_getter=lambda p: (0, 0, -.25, 0))
        
    def set_zooming_wheel(self):
        """Set zooming bindings with the wheel."""
        # Zooming: wheel
        self.set('Wheel', 'Zoom',
                    param_getter=lambda p: (
                                    p["wheel"]*.002, 
                                    p["mouse_position"][0],
                                    p["wheel"]*.002, 
                                    p["mouse_position"][1]))
        
    def set_reset(self):
        """Set reset bindings."""
        # Reset view
        self.set('KeyPress', 'Reset', key='R')
        # Reset zoom
        self.set('DoubleClick', 'Reset')
        
    def initialize(self):
        """Initialize all bindings. Can be overriden."""
        self.set_base_cursor()
        self.set_widget()
        # panning
        self.set_panning_mouse()
        self.set_panning_keyboard()
        # zooming
        self.set_zooming_mouse()
        self.set_zoombox_mouse()
        self.set_zoombox_keyboard()
        self.set_zooming_keyboard()
        self.set_zooming_wheel()
        # reset
        self.set_reset()
        # Extended bindings
        self.extend()
        
    def extend(self):
        """Initialize custom bindings. Can be overriden."""
        pass
        
        