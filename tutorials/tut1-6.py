"""Tutorial 1.6: Bar plots.

In this tutorial we show how to plot efficiently several bar plots.

"""

import numpy.random as rnd
from galry import *

# We generate 10 random bar plots of 100 values in each.
values = rnd.rand(10, 100)

# Offsets of histograms: we stack them vertically.
offset = np.vstack((np.zeros(10), np.arange(10))).T

# We plot the histograms with random colors.
barplot(values, offset=offset, color=rnd.rand(10, 3))

show()