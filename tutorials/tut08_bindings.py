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
        # Deactivate constraining the navigation into [-1, 1]^2 (the default).
        self.interaction_manager.constrain_navigation = False
        
        n = 10000
        
        # We add a plot with random points.
        self.create_dataset(n)
        self.set_data(position=.2 * rdn.randn(n, 2))

# We define a customized binding by deriving a class from the base class
# `ActionEventBindingSet`. This class links individual user actions to
# interaction events. It defines an interaction mode, with a base mouse cursor,
# and a set of bindings.
class MyBinding(ActionEventBindingSet):
    
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
show_basic_window(bindings=MyBinding, paint_manager=MyPaintManager)
