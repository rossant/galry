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
        
        # We add text at the center of the widget.
        text = "Hello world! :)"
        
        # Here we add a dataset on the screen. A dataset is an object drawn
        # on the screen that consists in a homogeneous set of primitives.
        # A text, a set of rectangles, triangles, points, curves, textures
        # are examples of datasets. A dataset is defined by its template, which
        # describes how this object is rendered on the screen. The template 
        # can have several slots containing data or parameters, that can be
        # filled here with the `set_data` method.
        self.create_dataset(TextTemplate, text=text)
                
# We show a basic QT window with a custom galry widget.
# This widget has our custom `MyPaintManager` class as a paint manager.
# The window has a size (500, 500) and a position (100, 100) on the screen.
show_basic_window(paint_manager=MyPaintManager,
                  size=(500., 500.), position=(100., 100.),
                  constrain_navigation=False)
