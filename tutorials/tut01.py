"""Tutorial 01: Pylab-style plotting.

In this tutorial, we show how to plot a basic figure with a pylab-/matlab- 
like high-level interface.

"""
# With this import syntax, all variables in Galry and Numpy are imported,
# like with from pylab import * in Matplotlib.
from galry import *

# We define a simple curve with the graph x -> sin(x) on [-10., 10.].
x = linspace(-10., 10., 10000)
y = sin(x)

# We plot this function.
plot(x, y)

# Finally, we show the window. The real job happens here.
show()
