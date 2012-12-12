import inspect
from collections import OrderedDict as odict
import numpy as np
from galry import Manager, TextVisual, get_color



__all__ = ['EventProcessor']


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
        
        
    # Paint Manager methods
    # ---------------------
    def _get_paint_manager(self):
        return self.interaction_manager.paint_manager
    paint_manager = property(_get_paint_manager)
        
    def set_data(self, *args, **kwargs):
        # shortcut to paint_manager.set_data
        return self.parent.paint_manager.set_data(*args, **kwargs)
        
    def get_visual(self, name):
        return self.parent.paint_manager.get_visual(name)
        
    def add_visual(self, *args, **kwargs):
        name = kwargs.get('name')
        if not self.get_visual(name):
            self.parent.paint_manager.add_visual(*args, **kwargs)
        
        
    # Cursor methods
    # --------------
    def set_cursor(self, cursor):
        self.cursor = cursor
        
    def get_cursor(self):
        """Return the current cursor."""
        # if self.cursor is None:
            # return self.base_cursor
        # else:
        return self.cursor
        
        
    # Handlers methods
    # ----------------
    def register(self, event, method):
        """Register a handler for the event."""
        self.handlers[event] = method
        
    def registered(self, event):
        """Return whether the specified event has been registered by this
        processor."""
        return self.handlers.get(event, None) is not None
        
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
                fig = self.interaction_manager.figure
                # HACK: give access to paint_manager.set_data to the figure,
                # so that event processors can change the data
                fig.set_data = self.parent.paint_manager.set_data
                # here, we are using the high level interface and figure
                # is the Figure object we pass to this function
                method(fig, parameter)

    def process_none(self):
        """Process the None event, occuring when there's no event, or when
        an event has just finished."""
        self.process(None, None)
        
        
    # Methods to override
    # -------------------
    def initialize(self, *args, **kwargs):
        """Initialize the event processor by calling self.register to register
        handlers for different events."""
        pass
        
        
