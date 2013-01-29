"""3D cube example."""

from galry import *
import numpy as np

# cube creation function
def create_cube(color, scale=1.):
    """Create a cube as a set of independent triangles.
    
    Arguments:
      * color: the colors of each face, as a 6*4 array.
      * scale: the scale of the cube, the ridge length is 2*scale.
    
    Returns:
      * position: a Nx3 array with the positions of the vertices.
      * normal: a Nx3 array with the normals for each vertex.
      * color: a Nx3 array with the color for each vertex.
    
    """
    position = np.array([
        # Front
        [-1., -1., -1.],
        [1., -1., -1.],
        [-1., 1., -1.],
        
        [1., 1., -1.],
        [-1., 1., -1.],
        [1., -1., -1.],
        
        # Right
        [1., -1., -1.],
        [1., -1., 1.],
        [1., 1., -1.],
        
        [1., 1., 1.],
        [1., 1., -1.],
        [1., -1., 1.],
        
        # Back
        [1., -1., 1.],
        [-1., -1., 1.],
        [1., 1., 1.],
        
        [-1., 1., 1.],
        [1., 1., 1.],
        [-1., -1., 1.],
        
        # Left
        [-1., -1., 1.],
        [-1., -1., -1.],
        [-1., 1., 1.],
        
        [-1., 1., -1.],
        [-1., 1., 1.],
        [-1., -1., -1.],
        
        # Bottom
        [1., -1., 1.],
        [1., -1., -1.],
        [-1., -1., 1.],
        
        [-1., -1., -1.],
        [-1., -1., 1.],
        [1., -1., -1.],
        
        # Top
        [-1., 1., -1.],
        [-1., 1., 1.],
        [1., 1., -1.],
        
        [1., 1., 1.],
        [1., 1., -1.],
        [-1., 1., 1.],
    ])
    
    normal = np.array([
        # Front
        [0., 0., -1.],
        [0., 0., -1.],
        [0., 0., -1.],

        [0., 0., -1.],
        [0., 0., -1.],
        [0., 0., -1.],
        
        # Right
        [1., 0., 0.],
        [1., 0., 0.],
        [1., 0., 0.],

        [1., 0., 0.],
        [1., 0., 0.],
        [1., 0., 0.],
        
        # Back
        [0., 0., 1.],
        [0., 0., 1.],
        [0., 0., 1.],

        [0., 0., 1.],
        [0., 0., 1.],
        [0., 0., 1.],
        
        # Left
        [-1., 0., 0.],
        [-1., 0., 0.],
        [-1., 0., 0.],
        
        [-1., 0., 0.],
        [-1., 0., 0.],
        [-1., 0., 0.],
        
        # Bottom
        [0., -1., 0.],
        [0., -1., 0.],
        [0., -1., 0.],
        
        [0., -1., 0.],
        [0., -1., 0.],
        [0., -1., 0.],
        
        # Top
        [0., 1., 0.],
        [0., 1., 0.],
        [0., 1., 0.],
        
        [0., 1., 0.],
        [0., 1., 0.],
        [0., 1., 0.],
    ])    
    position *= scale
    color = np.repeat(color, 6, axis=0)
    return position, normal, color

# face colors
color = np.ones((6, 4))
color[0,[0,1]] = 0
color[1,[0,2]] = 0
color[2,[1,2]] = 0
color[3,[0]] = 0
color[4,[1]] = 0
color[5,[2]] = 0

# create the cube
position, normal, color = create_cube(color)

# render it as a set of triangles
mesh(position=position, color=color, normal=normal)
   
show()
