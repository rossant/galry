import inspect
import numpy as np
from processor import EventProcessor
from galry import Manager, TextVisual, get_color, ordict


class DefaultEventProcessor(EventProcessor):
    def initialize(self):
        self.register('Fullscreen', self.process_toggle_fullscreen)
        self.register('Help', self.process_help_event)
        self.help_visible = False
        
    def process_toggle_fullscreen(self, parameter):
        self.parent.toggle_fullscreen()
        
    def process_help_event(self, parameter):
        self.help_visible = not(self.help_visible)
        text = self.parent.binding_manager.get().get_text()
        self.set_data(visual='help', visible=self.help_visible, text=text)
        
        