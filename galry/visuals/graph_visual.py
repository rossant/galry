from visual import CompoundVisual, RefVar
from sprite_visual import SpriteVisual
from plot_visual import PlotVisual
from galry import get_color
import numpy as np

__all__ = ['GraphVisual']

def get_tex(n):
    """Create a texture for the nodes. It may be simpler to just use an image!
    
    It returns a n*n*4 Numpy array with values in [0, 1]. The transparency
    channel should contain the shape of the node, where the other channels
    should encode the color.
    
    """
    tex = np.ones((n, n, 4))
    tex[:,:,0] = 1
    x = np.linspace(-1., 1., n)
    X, Y = np.meshgrid(x, x)
    R = X ** 2 + Y ** 2
    R = np.minimum(1, 3 * np.exp(-3*R))
    tex[:,:,-1] = R
    return tex

class GraphVisual(CompoundVisual):
    def initialize(self, position=None, edges=None, color=None,
        edges_color=None, node_size=None, autocolor=None, **kwargs):
        
        if autocolor is not None:
            color = get_color(autocolor)
        
        if node_size is None:
            node_size = 8.
        if color is None:
            color = (1., 1., 1., .25)

        # relative indexing
        edges = np.array(edges, dtype=np.int32).reshape((-1, 2))
        # uedges = np.unique(edges)
        # edges[:,0] = np.digitize(edges[:,0], uedges) - 1
        # edges[:,1] = np.digitize(edges[:,1], uedges) - 1
        
        # edges
        self.add_visual(PlotVisual, position=position,
            primitive_type='LINES', color=edges_color,
            index=edges.ravel(), name='edges')
        
        if isinstance(node_size, np.ndarray):
            texsize = int(node_size.max())
        else:
            texsize = node_size
        
        # nodes
        self.add_visual(SpriteVisual,
            position=RefVar(self.name + '_edges', 'position'),
            point_size=node_size, zoomable=True,
            color=color, texture=get_tex(texsize * 4), name='nodes')

