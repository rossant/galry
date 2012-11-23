"""Tutorial 08: Customizing interaction bindings.

This tutorial shows how to customize bindings between user actions and
existing interaction events. The widget created here overrides the default
interaction system with navigation, and implements a custom one with
only zooming in one direction associated to the mouse user action.

"""

# We import galry.
from galry import *
import numpy.random as rdn

class MyPaintManager(PaintManager):
    def initialize(self):
        
        # We add a plot with random points.
        self.add_visual(PlotVisual, position=.2 * rdn.randn(10000, 2),
            primitive_type='POINTS')

# We define a customized binding by deriving a class from the base class
# `BindingSet`. This class links individual user actions to
# interaction events. It defines an interaction mode, with a base mouse cursor,
# and a set of bindings.
class MyBinding(BindingSet):
    
    # The initialize method can be overriden and defines the bindings by
    # making calls to the `set` method.
    def initialize(self):
        
        # We need to import cursors here and not at the beginning of the script
        # because QT must have been initialized before loading cursors.
        # from galry import cursors
        
        # We specify a custom base cursor for this interaction mode.
        self.set_base_cursor(cursors.MagnifyingGlassCursor)
        
        # We bind the action corresponding to a mouse move while pressing
        # the left button, with the zooming event. The parameters associated
        # to the zooming event processor are (dx, px, dy, py) where (dx, dy)
        # contain the amount of zoom in the two axes, and (px, py) are the
        # coordinates of the zoom center.
        self.set(UserActions.LeftButtonMouseMoveAction,
                InteractionEvents.ZoomEvent,
                param_getter=lambda p: (p["mouse_position_diff"][0],
                                        p["mouse_press_position"][0],
                                        0, 
                                        0))
        
# We pass our custom binding to the widget through the `bindings` argument.
show_basic_window(bindings=MyBinding, paint_manager=MyPaintManager,
                  constrain_navigation=False)
