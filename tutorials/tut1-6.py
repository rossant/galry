"""Tutorial 1.6: 3D mesh.

In this tutorial we show how to plot a 3D mesh.

It is adapted from an example in the Glumpy package:
http://code.google.com/p/glumpy/

"""

from galry import *


def load_obj(filename):
    """Load vertices and faces from a wavefront .obj file and generate
    normals.
    
    """
    data = np.genfromtxt(filename, dtype=[('type', np.character, 1),
                                          ('points', np.float32, 3)])

    # Get vertices and faces
    vertices = data['points'][data['type'] == 'v']
    faces = (data['points'][data['type'] == 'f']-1).astype(np.uint32)

    # Build normals
    T = vertices[faces]
    N = np.cross(T[::,1 ]-T[::,0], T[::,2]-T[::,0])
    L = np.sqrt(N[:,0]**2+N[:,1]**2+N[:,2]**2)
    N /= L[:, np.newaxis]
    normals = np.zeros(vertices.shape)
    normals[faces[:,0]] += N
    normals[faces[:,1]] += N
    normals[faces[:,2]] += N
    L = np.sqrt(normals[:,0]**2+normals[:,1]**2+normals[:,2]**2)
    normals /= L[:, np.newaxis]

    # Scale vertices such that object is contained in [-1:+1,-1:+1,-1:+1]
    vmin, vmax =  vertices.min(), vertices.max()
    vertices = 2*(vertices-vmin)/(vmax-vmin) - 1

    return vertices, normals, faces


vertices, normals, faces = load_obj("images/mesh.obj")
n = len(vertices)

# face colors
color = (vertices + 1) / 2.
color = np.hstack((color, np.ones((n, 1))))

mesh(position=vertices, color=color, normal=normals, index=faces.ravel())


show()


