import inspect
# from collections import OrderedDict as odict
import numpy as np
from galry import Manager, TextVisual, get_color, NavigationEventProcessor, \
    DefaultEventProcessor, EventProcessor, GridEventProcessor, ordict, \
    log_debug, log_info, log_warn


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
        self.processors = ordict()
        self.initialize_default(
            constrain_navigation=self.parent.constrain_navigation,
            momentum=self.parent.momentum)
        self.initialize()
        
    def initialize(self):
        """Initialize the InteractionManager.
        
        To be overriden.
        """
        pass
        
    def initialize_default(self, **kwargs):
        pass
        
        
    # Processor methods
    # -----------------
    def get_processors(self):
        """Return all processors."""
        return self.processors
        
    def get_processor(self, name):
        """Return a processor from its name."""
        if name is None:
            name = 'processor0'
        return self.processors.get(name, None)
        
    def add_processor(self, cls, *args, **kwargs):
        """Add a new processor, which handles processing of interaction events.
        Several processors can be defined in an InteractionManager instance.
        One event can be handled by several processors.
        """
        # get the name of the visual from kwargs
        name = kwargs.pop('name', 'processor%d' % (len(self.get_processors())))
        if self.get_processor(name):
            raise ValueError("Processor name '%s' already exists." % name)
        activated = kwargs.pop('activated', True)
        processor = cls(self, *args, **kwargs)
        self.processors[name] = processor
        processor.activate(activated)
        return processor
        
    def add_default_processor(self):
        """Add a default processor, useful to add handlers for events
        in the InteractionManager without explicitely creating a new
        processor."""
        return self.add_processor(EventProcessor, name='default_processor')
        
    def register(self, event, method):
        """Register a new handler for an event, using the manager's default
        processor."""
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
                if processor.activated and processor.registered(event):
                    # print name, event
                    processor.process(event, parameter)
                    cursor = processor.get_cursor()
                    if self.cursor is None:
                        self.cursor = cursor
        self.prev_event = event
        
    def get_cursor(self):
        return self.cursor
        
        
        
        
        