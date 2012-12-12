import inspect
from collections import OrderedDict as odict
import numpy as np
from processor import EventProcessor
from galry import Manager, TextVisual, get_color


class WidgetEventProcessor(EventProcessor):
    def initialize(self):
        self.register('ToggleFullscreen', self.process_toggle_fullscreen)
        # self.register('CloseWidget', self.process_close_widget)
        self.register('Help', self.process_help_event)
        self.help_visible = False
        
    def process_toggle_fullscreen(self, parameter):
        self.parent.toggle_fullscreen()
        
    # def process_close_widget(self, parameter):
        # self.parent.close_widget()
        
    def process_help_event(self, parameter):
        self.help_visible = not(self.help_visible)
        
        self.set_data(visual='help', visible=self.help_visible,
            text=self.get_help_text())
        
    def get_help_text(self):
        return self.parent.binding_manager.get().get_text()
        

