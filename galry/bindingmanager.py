from qtools.qtpy import QtCore, QtGui
from qtools.qtpy.QtCore import Qt 
from galry import Manager, ordict
import numpy as np


__all__ = ['BindingManager', 'Bindings']


class BindingManager(Manager):
    """Manager several sets of bindings (or interaction modes) and allows
    to switch between several modes.
    """
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
        if not isinstance(binding, Bindings):
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
  
  
class Bindings(object):
    """Base class for action-events bindings set.
    
    An instance of this class contains all bindings between user actions, and
    interaction events, that are possible within a given interaction mode. 
    An interaction mode is entirely defined by such set of bindings.
    The GalryWidget provides a mechanism for switching between successive
    modes.
    
    """
    def __init__(self):
        self.base_cursor = 'ArrowCursor'
        self.text = None
        self.binding = ordict()
        self.descriptions = ordict()
        self.initialize_default()
        self.initialize()
        
    def set_base_cursor(self, cursor=None):
        """Define the base cursor in this mode."""
        if cursor is None:
            cursor = 'OpenHandCursor'
        # set the base cursor
        self.base_cursor = cursor

    def get_base_cursor(self):
        return self.base_cursor
        
    def initialize_default(self):
        """Set bindings that are common to any interaction mode."""
        self.set('KeyPress', 'SwitchInteractionMode', key='I')
        
    def initialize(self):
        """Registers all bindings through commands to self.set().
        
        To be overriden.
        
        """
        pass
        
    def set(self, action, event, key_modifier=None, key=None,
                            param_getter=None, description=None):
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
        # if param_getter is a value and not a function, we convert it
        # to a constant function
        if not hasattr(param_getter, '__call__'):
            param = param_getter
            param_getter = lambda p: param
        self.binding[(action, key_modifier, key)] = (event, param_getter)
        if description:
            self.descriptions[(action, key_modifier, key)] = description
        
    def get(self, action, key_modifier=None, key=None):
        """Return the event and parameter getter function associated to
        a function.
        
        Arguments:
          * action: the user action.
          * key_modifier=None: the key modifier.
          * key=None: the key if the action is `KeyPress`.
          
        """
        return self.binding.get((action, key_modifier, key), (None, None))
    
    def get_description(self, action, key_modifier=None, key=None):
        return self.descriptions.get((action, key_modifier, key), None)
    
    
    # Help methods
    # ------------
    def generate_text(self):
        special_keys = {
            None: '',
            QtCore.Qt.Key_Control: 'CTRL',
            QtCore.Qt.Key_Shift: 'SHIFT',
            QtCore.Qt.Key_Alt: 'ALT',
        }
        
        texts = {}
        for (action, key_modifier, key), (event, _) in self.binding.iteritems():
            desc = self.get_description(action, key_modifier, key)
            
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
            
            if desc:
                bstr += ' ' + desc
            
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
    
    