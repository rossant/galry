"""Benchmark 01: Displaying points.

"""

from galry import *
figure(display_fps=True)
x, y = .2 * random.randn(2, 1e6)
plot(x, y, ',', ms=1)
show()
