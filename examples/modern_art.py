"""Modern art."""
from galry import *
import numpy.random as rdn

figure(constrain_ratio=True, antialiasing=True)

# random positions
positions = .25 * rdn.randn(1000, 2)

# random colors
colors = rdn.rand(len(positions),4)

# TRIANGLES: three consecutive points = one triangle, no overlap
plot(primitive_type='TRIANGLES', position=positions, color=colors)

show()
