from galry.processors import NavigationEventProcessor, DefaultEventProcessor
from galry import PaintManager, InteractionManager, GridEventProcessor, \
    RectanglesVisual, GridVisual, TextVisual, Bindings, get_color


class DefaultInteractionManager(InteractionManager):
    def initialize_default(self, **kwargs):
        super(DefaultInteractionManager, self).initialize_default(**kwargs)
        self.add_processor(DefaultEventProcessor, name='widget')


class DefaultPaintManager(PaintManager):
    def initialize_default(self, **kwargs):
        super(DefaultPaintManager, self).initialize_default(**kwargs)
        # Help
        if self.parent.activate_help:
            self.add_visual(TextVisual, coordinates=(-.95, .95),
                            fontsize=14, color=get_color('w'),
                            interline=37., letter_spacing=320.,
                            depth=-1., background_transparent=False,
                            is_static=True, prevent_constrain=True,
                            text='', name='help', visible=False)
        
        
class DefaultBindings(Bindings):
    def set_fullscreen(self):
        self.set('KeyPress', 'Fullscreen', key='F')
        
    def set_help(self):
        self.set('KeyPress', 'Help', key='H')
    
    def initialize_default(self):
        super(DefaultBindings, self).initialize_default()
        self.set_fullscreen()
        self.set_help()
        
        
        