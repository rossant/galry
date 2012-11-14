from python_qt_binding.QtCore import Qt 
import cursors
import numpy as np
from interactionevents import InteractionEvents as events
from useractions import UserActions as actions

__all__ = ['BindingManager', 'BindingSet', 'DefaultBindingSet']

class BindingManager(object):
    """Manager several sets of bindings (or interaction modes) and allows
    to switch between several modes.
    """
    def __init__(self):
        self.reset()
    
    def reset(self):
        """Reset the modes."""
        self.bindings = []
        self.index = 0
    
    def add(self, *bindings):
        """Add one or several bindings to the binding manager.
        
        Arguments:
          * bindings: a list of classes deriving from UserActionBinding.
          
        """
        self.bindings.extend(bindings)
        
    def remove(self, binding):
        """Remove a binding.
        
        Arguments:
          * binding: the binding to remove.
          
        """
        if binding in self.bindings:
            self.bindings.remove(binding)
            
    def set(self, binding):
        """Set the given binding as the active one.
        
        Arguments:
          * binding: the current binding.
          
        """
        self.add(binding)
        self.index = self.bindings.index(binding)
            
    def get(self):
        """Return the current binding."""
        if self.index < len(self.bindings):
            return self.bindings[self.index]
        else:
            return None
            
    def switch(self):
        """Switch the active binding. The bindings cycle through all bindings.
        
        """
        self.index = np.mod(self.index + 1, len(self.bindings))
        return self.get()
  
class BindingSet(object):
    """Base class for action-events bindings set.
    
    An instance of this class contains all bindings between user actions, and
    interaction events, that are possible within a given interaction mode. 
    An interaction mode is entirely defined by such set of bindings.
    The GalryWidget provides a mechanism for switching between successive
    modes.
    
    """
    def __init__(self):
        # HACK: a QApplication needs to be constructed for creating Pixmap
        # cursors, so we load (and create the cursors) here
        # if "cursors" not in globals():
            # import cursors
        self.base_cursor = cursors.ArrowCursor
        
        self.binding = {}
        self.set_common_bindings()
        self.initialize()
        
    def set_base_cursor(self, cursor=None):
        """Define the base cursor in this mode."""
        if cursor is None:
            cursor = cursors.OpenHandCursor
        # set the base cursor
        self.base_cursor = cursor

    def set_common_bindings(self):
        """Set bindings that are common to any interaction mode."""
        self.set(actions.KeyPressAction, events.SwitchInteractionModeEvent,
                    key=Qt.Key_M)
        
    def initialize(self):
        """Registers all bindings through commands to self.set().
        
        To be overriden.
        
        """
        pass
        
    def set(self, action, event, key_modifier=None, key=None,
                            param_getter=None):
        """Register an action-event binding.
        
        Arguments:
          * action: a UserActions enum value.
          * event: a InteractionEvents enum value.
          * key_modifier=None: the key modifier as a Qt.Key_? enum value.
          * key=None: when the action is KeyPressAction, the key that was 
            pressed.
          * param_getter=None: a function that takes an ActionParameters dict 
            as argument and returns a parameter object that will be passed 
            to InteractionManager.process_event(event, parameter)
            
        """
        self.binding[(action, key_modifier, key)] = (event, param_getter)
        
    def get(self, action, key_modifier=None, key=None):
        """Return the event and parameter getter function associated to
        a function.
        
        Arguments:
          * action: the user action.
          * key_modifier=None: the key modifier.
          * key=None: the key if the action is `KeyPressAction`.
          
        """
        return self.binding.get((action, key_modifier, key), (None, None))
     
class DefaultBindingSet(BindingSet):
    """A default set of bindings for interactive navigation.
    
    This binding set makes use of the keyboard and the mouse.
    
    """
    def set_panning_mouse(self):
        """Set panning bindings with the mouse."""
        # Panning: left button mouse
        self.set(actions.LeftButtonMouseMoveAction, events.PanEvent,
                    param_getter=lambda p: (p["mouse_position_diff"][0],
                                            p["mouse_position_diff"][1]))
        
    def set_panning_keyboard(self):
        """Set panning bindings with the keyboard."""
        # Panning: keyboard arrows
        self.set(actions.KeyPressAction, events.PanEvent,
                    key=Qt.Key_Left,
                    param_getter=lambda p: (.24, 0))
        self.set(actions.KeyPressAction, events.PanEvent,
                    key=Qt.Key_Right,
                    param_getter=lambda p: (-.24, 0))
        self.set(actions.KeyPressAction, events.PanEvent,
                    key=Qt.Key_Up,
                    param_getter=lambda p: (0, -.24))
        self.set(actions.KeyPressAction, events.PanEvent,
                    key=Qt.Key_Down,
                    param_getter=lambda p: (0, .24))
                
    def set_zooming_mouse(self):
        """Set zooming bindings with the mouse."""
        # Zooming: right button mouse
        self.set(actions.RightButtonMouseMoveAction, events.ZoomEvent,
                    param_getter=lambda p: (p["mouse_position_diff"][0]*2.5,
                                            p["mouse_press_position"][0],
                                            p["mouse_position_diff"][1]*2.5,
                                            p["mouse_press_position"][1]))
    
    def set_zoombox_mouse(self):
        """Set zoombox bindings with the mouse."""
        # Zooming: zoombox (drag and drop)
        self.set(actions.MiddleButtonMouseMoveAction, events.ZoomBoxEvent,
                    param_getter=lambda p: (p["mouse_press_position"][0],
                                            p["mouse_press_position"][1],
                                            p["mouse_position"][0],
                                            p["mouse_position"][1]))
    
    def set_zoombox_keyboard(self):
        """Set zoombox bindings with the keyboard."""
        # Idem but with CTRL + left button mouse 
        self.set(actions.LeftButtonMouseMoveAction, events.ZoomBoxEvent,
                    key_modifier=Qt.Key_Control,
                    param_getter=lambda p: (p["mouse_press_position"][0],
                                            p["mouse_press_position"][1],
                                            p["mouse_position"][0],
                                            p["mouse_position"][1]))
                 
    def set_zooming_keyboard(self):
        """Set zooming bindings with the keyboard."""
        # Zooming: ALT + key arrows
        self.set(actions.KeyPressAction, events.ZoomEvent,
                    key=Qt.Key_Left, key_modifier=Qt.Key_Control, 
                    param_getter=lambda p: (-.25, 0, 0, 0))
        self.set(actions.KeyPressAction, events.ZoomEvent,
                    key=Qt.Key_Right, key_modifier=Qt.Key_Control, 
                    param_getter=lambda p: (.25, 0, 0, 0))
        self.set(actions.KeyPressAction, events.ZoomEvent,
                    key=Qt.Key_Up, key_modifier=Qt.Key_Control, 
                    param_getter=lambda p: (0, 0, .25, 0))
        self.set(actions.KeyPressAction, events.ZoomEvent,
                    key=Qt.Key_Down, key_modifier=Qt.Key_Control, 
                    param_getter=lambda p: (0, 0, -.25, 0))
        
    def set_zooming_wheel(self):
        """Set zooming bindings with the wheel."""
        # Zooming: wheel
        self.set(actions.WheelAction, events.ZoomEvent,
                    param_getter=lambda p: (
                                    p["wheel"]*.002, 
                                    p["mouse_position"][0],
                                    p["wheel"]*.002, 
                                    p["mouse_position"][1]))
        
    def set_reset(self):
        """Set reset bindings."""
        # Reset view
        self.set(actions.KeyPressAction, events.ResetEvent, key=Qt.Key_R)
        # Reset zoom
        self.set(actions.DoubleClickAction, events.ResetEvent)
        
    def initialize(self):
        """Initialize all bindings. Can be overriden."""
        self.set_base_cursor()
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
        