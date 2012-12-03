"""Tutorial 09: Defining new interaction events.

This tutorial shows how to define and implement new interaction events.
Pressing the space bar toggles between uniform or Gaussian random data.

"""

# We import galry.
from galry import *
import numpy.random as rdn

# This function generates Gaussian data.
def get_gaussian(n):
    """Return random data generated according to a Gaussian distribution."""
    return .29 * rdn.randn(n, 2)

# This function generates uniform data.    
def get_uniform(n):
    """Return random data generated according to an uniform distribution."""
    return rdn.rand(n, 2) - .5

class MyPaintManager(PaintManager):
    # Number of points.
    n = 10000.
    
    # This variable allows to toggle between gaussian and uniform laws.
    gaussian = False
    
    # A call to this function updates data in GPU memory.
    def update_data(self):
        """Change data from uniform to Gaussian."""
        if self.gaussian:
            newdata = get_gaussian(self.n)
        else:
            newdata = get_uniform(self.n)
        
        # We update the buffer by specifying the name, visual, and
        # the updated data. This array must have the exact same
        # dimensions as the original data in the buffer.
        self.set_data(position=newdata)
        
        # Toggle between gaussian and uniform laws.
        self.gaussian = not self.gaussian
    
    def initialize(self):
        
        # We add a plot with random points.
        data = get_gaussian(self.n)
        self.add_visual(PlotVisual, position=data, primitive_type='POINTS')

# We create a class deriving from `InteractionManager` that processes the
# newly defined event.
class MyInteractionManager(InteractionManager):
    # The method `process_custom_event` processes the newly created events
    # when they are raised. The first parameter `event` is an element of the
    # an identifier string, whereas `parameter` contains the parameters of
    # the associated user action that was returned by the `param_getter` 
    # function defined in the binding.
    def process_custom_event(self, event, parameter):
        # Here, we call the `update_data` method of the PaintManager whenever
        # this event is raised. We don't use the parameter here.
        if event == "ChangeLawEvent":
            self.paint_manager.update_data()

# We define a custom interaction mode by deriving from the default one.
# The `DefaultBindingSet` implements navigation events.
class MyBinding(DefaultBindingSet):
    # The `extend` method allows to define new bindings.
    def extend(self):
        # This binding associates pressing the space button with the 
        # `ChangeLawEvent`.
        self.set(UserActions.KeyPressAction, "ChangeLawEvent",
                 key=QtCore.Qt.Key_Space)

print "Press space!"
# We specify the custom paint manager and interaction manager, and the 
# custom bindings.
show_basic_window(paint_manager=MyPaintManager,
                    interaction_manager=MyInteractionManager,
                    bindings=MyBinding)
