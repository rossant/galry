"""Tutorial 1.7: 3D mesh.

In this tutorial we show how to plot a 3D mesh.

It is adapted from an example in the Glumpy package:
http://code.google.com/p/glumpy/

"""

from galry import *
from numpy import *

# load a 3D mesh from a OBJ file
vertices, normals, faces = load_mesh("images/mesh.obj")
n = len(vertices)

# face colors
color = (vertices + 1) / 2.
color = np.hstack((color, np.ones((n, 1))))

# display the mesf
mesh(position=vertices, color=color, normal=normals, index=faces.ravel())

show()
