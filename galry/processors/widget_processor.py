import inspect
from collections import OrderedDict as odict
import numpy as np
from processor import EventProcessor
from galry import Manager, TextVisual, get_color


class WidgetEventProcessor(EventProcessor):
    def initialize(self):
        self.register('ToggleFullscreen', self.process_toggle_fullscreen)
        self.register('Grid', self.process_grid_event)
        self.register('Help', self.process_help_event)
        self.help_visible = False
        self.grid_visible = False
        
    def process_grid_event(self, parameter):
        self.grid_visible = not(self.grid_visible)
        self.set_data(visual='grid_lines', visible=self.grid_visible)
        self.set_data(visual='grid_text', visible=self.grid_visible)
    
    def process_toggle_fullscreen(self, parameter):
        self.parent.toggle_fullscreen()
        
    def process_help_event(self, parameter):
        self.help_visible = not(self.help_visible)
        text = self.parent.binding_manager.get().get_text()
        self.set_data(visual='help', visible=self.help_visible, text=text)
        
        