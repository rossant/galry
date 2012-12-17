"""Tutorial 1.2: Multiple curves.

In this tutorial, we show how to plot several curves efficiently.

"""

from galry import *
from numpy import *

# We'll plot 10 curves with 10,000 points in each.
m = 10
n = 10000

# z contains m signals with n random values in each. Each row is a signal.
z = .1 * random.randn(m, n)

# We shift the y coordinates in each line, so that each signal is shown
# separately.
z += arange(m).reshape((-1, 1))

# `color` is an m x 3 matrix, where each line contains the RGB components
# of the corresponding line. We also could use an alpha channel
# (transparency) with an m x 4 matrix.
color = random.rand(m, 3)

# We disable zooming out more than what the figure contains.
figure(constrain_navigation=True)

# We plot all signals and specify the color.
# Note: it is much faster to have a single plot command, rather than one plot
# per curve, especially if there are a lot of curves (like hundreds or
# thousands).
plot(z, color=color, options='r')

# We show the figure.
show()
