"""Benchmark 01: Displaying points.

"""

from galry import *
from numpy import *
from numpy.random import *

figure(display_fps=True)
x, y = .2 * randn(2, 1e6)
plot(x, y, ',', ms=1)
show()
