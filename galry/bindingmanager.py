from python_qt_binding import QtCore, QtGui
from python_qt_binding.QtCore import Qt 
from collections import OrderedDict as odict
from galry import Manager
import numpy as np


__all__ = ['BindingManager', 'BindingSet', 'DefaultBindingSet']


class BindingManager(Manager):
    """Manager several sets of bindings (or interaction modes) and allows
    to switch between several modes.
    """
    # def __init__(self, parent):
        # self.parent = parent
        # self.reset()
    
    def reset(self):
        """Reset the modes."""
        self.bindings = []
        self.index = 0
    
    def add(self, *bindings):
        """Add one or several bindings to the binding manager.
        
        Arguments:
          * bindings: a list of classes deriving from UserActionBinding.
          
        """
        bindings = [b for b in bindings if b not in self.bindings]
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
        if not isinstance(binding, BindingSet):
            # here, we assume that binding is a class, so we take the first
            # existing binding that is an instance of this class
            binding = [b for b in self.bindings if isinstance(b, binding)][0]
        self.add(binding)
        self.index = self.bindings.index(binding)
        return self.get()
            
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
        self.base_cursor = 'ArrowCursor'
        self.text = None
        self.binding = odict()
        self.set_common_bindings()
        self.initialize()
        
    def set_base_cursor(self, cursor=None):
        """Define the base cursor in this mode."""
        if cursor is None:
            cursor = 'OpenHandCursor'
        # set the base cursor
        self.base_cursor = cursor

    def get_base_cursor(self):
        return self.base_cursor
        
    def set_common_bindings(self):
        """Set bindings that are common to any interaction mode."""
        self.set('KeyPress', 'SwitchInteractionMode',
                    key='I')
        
    def initialize(self):
        """Registers all bindings through commands to self.set().
        
        To be overriden.
        
        """
        pass
        
    def set(self, action, event, key_modifier=None, key=None,
                            param_getter=None):
        """Register an action-event binding.
        
        Arguments:
          * action: a UserAction string.
          * event: a InteractionEvent string.
          * key_modifier=None: the key modifier as a string.
          * key=None: when the action is KeyPress, the key that was 
            pressed.
          * param_getter=None: a function that takes an ActionParameters dict 
            as argument and returns a parameter object that will be passed 
            to InteractionManager.process_event(event, parameter)
            
        """
        if isinstance(key, basestring):
            key = getattr(Qt, 'Key_' + key)
        if isinstance(key_modifier, basestring):
            key_modifier = getattr(Qt, 'Key_' + key_modifier)
        self.binding[(action, key_modifier, key)] = (event, param_getter)
        
    def get(self, action, key_modifier=None, key=None):
        """Return the event and parameter getter function associated to
        a function.
        
        Arguments:
          * action: the user action.
          * key_modifier=None: the key modifier.
          * key=None: the key if the action is `KeyPress`.
          
        """
        return self.binding.get((action, key_modifier, key), (None, None))
    
    def generate_text(self):
        special_keys = {
            None: '',
            QtCore.Qt.Key_Control: 'CTRL',
            QtCore.Qt.Key_Shift: 'SHIFT',
            QtCore.Qt.Key_Alt: 'ALT',
        }
        
        texts = {}
        for (action, key_modifier, key), (event, _) in self.binding.iteritems():
            # key string
            if key:
                key = QtGui.QKeySequence(key).toString()
            else:
                key = ''
            
            # key modifier
            key_modifier = special_keys[key_modifier]
            if key_modifier:
                key_modifier = key_modifier + ' + '

            # get binding text
            if action == 'KeyPress':
                bstr = 'Press ' + key_modifier + key + ' : ' + event
            else:
                bstr = key_modifier + action + ' : ' + event
            
            if event not in texts:
                texts[event] = []
            texts[event].append(bstr)
            
        # sort events
        self.text = "\n".join(["\n".join(sorted(texts[key])) for key in sorted(texts.iterkeys())])
        
    
    def get_text(self):
        if not self.text:
            self.generate_text()
        return self.text
    
    def __repr__(self):
        return self.get_text()
    
    
class DefaultBindingSet(BindingSet):
    """A default set of bindings for interactive navigation.
    
    This binding set makes use of the keyboard and the mouse.
    
    """
    def set_widget(self):
        self.set('KeyPress', 'ToggleFullscreen', key='F')
        self.set('KeyPress', 'Help', key='H')
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
        