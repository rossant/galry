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
            node_size = 8
        if color is None:
            color = (1., 1., 1., .25)

        # relative indexing
        edges = np.array(edges, dtype=np.int32)
        uedges = np.unique(edges)
        uedges.sort()
        # m = uedges.max()
        # n = len(uedges)
        # indices = np.zeros(m + 1, dtype=np.int32)
        # indices[uedges] = np.arange(n)
        # # indices = np.arange(uedges.max() + 1)
        # # indices[edges.ravel()].reshape((-1, 2))
        # edges = indices[edges]
        for i, u in enumerate(uedges):
            edges[edges == u] = i
        
        # edges
        self.add_visual(PlotVisual, position=position,
            primitive_type='LINES', color=edges_color,
            index=edges.ravel(), name='edges')
        
        # nodes
        self.add_visual(SpriteVisual,
            position=RefVar(self.name + '_edges', 'position'),
            color=color, texture=get_tex(node_size), name='nodes')

