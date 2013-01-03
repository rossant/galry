"""Tutorial 1.1: Pylab-style plotting.

In this tutorial, we show how to plot a basic figure with a pylab-/matlab- 
like high-level interface.

"""

from galry import *
from numpy import *

# We define a curve x -> sin(x) on [-10., 10.].
x = linspace(-10., 10., 10000)
y = .5 * sin(x)

# We plot this function.
plot(x, y)

# We set the limits for the y-axis.
ylim(-1, 1)

# Experiment with the default user actions! All actions can be changed but
# this would be the subject of a more advanced tutorial.
print("Press H to see all keyboard shortcuts and mouse movements!")

# Finally, we show the window. Internally, the real job happens here.
show()
