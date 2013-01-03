"""Markers example."""

from galry import *
from numpy.random import *

# We generate 10,000 points randomly according to a standard normal random
# variable.
x, y = randn(2, 10000)

# We assign one color for each point, with random RGBA components.
color = rand(10000, 4)

# We plot x wrt. y, with a '+' marker of size 20 (in pixels).
plot(x, y, '+', ms=20, color=color)

# We specify the axes as (x0, x1, y0, y1).
axes(-5, -5, 5, 5)

show()
