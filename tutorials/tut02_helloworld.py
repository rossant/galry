"""Tutorial 02: Hello World!

This tutorial shows how to derive the `PaintManager`, how to add text in the
widget, and how to change the size and initial position of the window on the
screen.

"""

# We import galry.
from galry import *

# The PaintManager companion class handles everything related to rendering.
# We need to override it in order to do something useful.
class MyPaintManager(PaintManager):
    
    # The `initialize` method defines all objects to be painted. It is meant
    # to be overriden here.
    def initialize(self):
        
        # We just add text in the center of the widget.
        text = "Hello world! :)"
        self.create_dataset(TextTemplate, text_length=len(text))
        self.set_data(text=text)

        self.interaction_manager.constrain_navigation = False
                
# We show a basic QT window with a custom galry widget.
# This widget has our custom `MyPaintManager` class as a paint manager.
# The window has a size (500, 500) and a position (100, 100) on the screen.
show_basic_window(paint_manager=MyPaintManager,
                  size=(500., 500.), position=(100., 100.))
