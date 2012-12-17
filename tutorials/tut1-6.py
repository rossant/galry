"""Tutorial 1.6: Bar plots.

In this tutorial we show how to plot efficiently several bar plots.

"""

from galry import *
from numpy import *
from numpy.random import *

# We generate 10 random bar plots of 100 values in each.
values = rand(10, 100)

# Offsets of histograms: we stack them vertically.
offset = vstack((zeros(10), arange(10))).T

# We plot the histograms with random colors.
barplot(values, offset=offset, color=rand(10, 3))

show()
