"""Example with 3D points."""
from galry import *
import numpy as np

n = 100000
position = np.random.randn(n, 3)
color = np.random.rand(n, 4)
normal = np.zeros((n, 3))

vertex_shader = """
gl_Position = vec4(position, 1.0);
varying_color = color;
gl_PointSize = 1.0;
"""

figure()
mesh(position=position, color=color, normal=normal,
     primitive_type='POINTS',
     vertex_shader=vertex_shader)
show()

