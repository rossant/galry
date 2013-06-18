import numpy as np
from visual import Visual
from mesh_visual import MeshVisual

from galry.tools import hsv_to_rgb

def colormap(x):
    """Colorize a 2D grayscale array.
    
    Arguments: 
      * x:an NxM array with values in [0,1] 
    
    Returns:
      * y: an NxMx3 array with a rainbow color palette.
    
    """
    x = np.clip(x, 0., 1.)
    
    # initial and final gradient colors, here rainbow gradient
    col0 = np.array([.67, .91, .65]).reshape((1, 1, -1))
    col1 = np.array([0., 1., 1.]).reshape((1, 1, -1))
    
    col0 = np.tile(col0, x.shape + (1,))
    col1 = np.tile(col1, x.shape + (1,))
    
    x = np.tile(x.reshape(x.shape + (1,)), (1, 1, 3))
    
    return hsv_to_rgb(col0 + (col1 - col0) * x)

    
__all__ = ['SurfaceVisual']

class SurfaceVisual(MeshVisual):
    def initialize(self, Z, *args, **kwargs):
        
        assert Z.ndim == 2, "Z must have exactly two dimensions"
        
        n, m = Z.shape

        # generate grid
        x = np.linspace(-1., 1., m)
        y = np.linspace(-1., 1., n)
        X, Y = np.meshgrid(x, y)

        # generate vertices positions
        position = np.hstack((X.reshape((-1, 1)), Z.reshape((-1, 1)), Y.reshape((-1, 1)),))

        #color
        m, M = Z.min(), Z.max()
        if m != M:
            Znormalized = (Z - m) / (M - m)
        else:
            Znormalized = Z
        color = colormap(Znormalized).reshape((-1, 3))
        color = np.hstack((color, np.ones((n*n,1))))

        # normal
        U = np.dstack((X[:,1:] - X[:,:-1],
                       Y[:,1:] - Y[:,:-1],
                       Z[:,1:] - Z[:,:-1]))
        V = np.dstack((X[1:,:] - X[:-1,:],
                       Y[1:,:] - Y[:-1,:],
                       Z[1:,:] - Z[:-1,:]))
        U = np.hstack((U, U[:,-1,:].reshape((-1,1,3))))
        V = np.vstack((V, V[-1,:,:].reshape((1,-1,3))))
        W = np.cross(U, V)
        normal0 = W.reshape((-1, 3))
        normal = np.zeros_like(normal0)
        normal[:,0] = normal0[:,0]
        normal[:,1] = normal0[:,2]
        normal[:,2] = normal0[:,1]

        # tesselation of the grid
        index = []
        for i in xrange(n-1):
            for j in xrange(n-1):
                index.extend([i*n+j, (i+1)*n+j, i*n+j+1,
                              (i+1)*n+j, i*n+j+1, (i+1)*n+j+1])
        index = np.array(index)

        kwargs.update(
            position=position,
            normal=normal,
            color=color, 
            index=index,
        )        
        super(SurfaceVisual, self).initialize(*args, **kwargs)
    
        
    
    
    
    