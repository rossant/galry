import inspect
from collections import OrderedDict as odict
import numpy as np
from galry import Manager, TextVisual, get_color, NavigationEventProcessor, \
    WidgetEventProcessor, EventProcessor


__all__ = ['InteractionManager']


class InteractionManager(Manager):
    """This class implements the processing of the raised interaction events.
    
    To be overriden.
    
    """
    
    # Initialization methods
    # ----------------------
    def __init__(self, parent):
        super(InteractionManager, self).__init__(parent)
        self.cursor = None
        self.prev_event = None
        self.processors = odict()
        self.initialize_default(
            constrain_navigation=self.parent.constrain_navigation)
        self.initialize()
        
    def initialize(self):
        """Initialize the InteractionManager.
        
        To be overriden.
        """
        pass
        
    def initialize_default(self, constrain_navigation=False):
        self.add_processor(NavigationEventProcessor,
            constrain_navigation=constrain_navigation, name='navigation')
        self.add_processor(WidgetEventProcessor, name='widget')
        
        
    # Processor methods
    # -----------------
    def get_processors(self):
        return self.processors
        
    def get_processor(self, name):
        if name is None:
            name = 'processor0'
        return self.processors.get(name, None)
        
    def add_processor(self, cls, *args, **kwargs):
        # get the name of the visual from kwargs
        name = kwargs.pop('name', 'processor%d' % (len(self.get_processors())))
        if self.get_processor(name):
            raise ValueError("Processor name '%s' already exists." % name)
        processor = cls(self, *args, **kwargs)
        self.processors[name] = processor
        return processor
        
    def add_default_processor(self):
        return self.add_processor(EventProcessor, name='default_processor')
        
    def register(self, event, method):
        processor = self.get_processor('default_processor')
        if processor is None:
            processor = self.add_default_processor()
        processor.register(event, method)
        
        
    # Event processing methods
    # ------------------------
    def process_event(self, event, parameter):
        """Process an event.
        
        This is the main method of this class. It is called as soon as an 
        interaction event is raised by an user action.
        
        Arguments:
          * event: the event to process, an InteractionEvent string.
          * parameter: the parameter returned by the param_getter function
            specified in the related binding.
        
        """
        # process None events in all processors
        if event is None and self.prev_event is not None:
            for name, processor in self.get_processors().iteritems():
                processor.process_none()
            self.cursor = None
        
        # process events in all processors
        if event is not None:
            for name, processor in self.get_processors().iteritems():
                if processor.registered(event):
                    processor.process(event, parameter)
                    self.cursor = processor.get_cursor()
        
        self.prev_event = event
        
    def get_cursor(self):
        return self.cursor
        
        
        
        
        