from galry import *
import numpy.random as rdn
import networkx as nx

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

class GraphPaintManager(PaintManager):
    def initialize(self):
        
        # number of nodes
        n = 1000
        
        # we define a random graph with networkx
        g = nx.watts_strogatz_graph(n, 3, 0.5)
        # g = nx.erdos_renyi_graph(n, 0.01)
        # g = nx.complete_graph(n)
        
        # we compute the layout, ie the positions of the nodes, with
        # networkx, on the GPU. This might be a bottleneck when dealing with
        # large graphs, so one should consider doing that on the GPU is
        # possible.
        pos = nx.circular_layout(g)
        
        # get the array with the positions of all nodes
        positions = np.vstack([pos[i] for i in xrange(len(pos))]) - .5
        
        # positions = rdn.randn(n, 2) * .2
        
        # get the array with all edges
        edges = np.vstack(g.edges()).ravel()
        
        # random colors for the nodes
        color = np.random.rand(len(positions), 4)
        color[:,-1] = 1
        
        # colors of the edges
        coledges = (1., 1., 1., .1)
        
        # we begin with the edges: we use indexing with a single buffer
        # containing the positions of all nodes. The indices allow
        # to draw the lines between any two connected nodes, without using
        # too much memory on the GPU.
        self.add_visual(PlotVisual, position=positions,
            primitive_type='LINES', color=coledges, index=edges, name='edges')
        
        # Then we add the nodes, with one texture for each node. Moreover,
        # we use the same buffer than in the "edges" visual (nodes position)
        # by specifiying that we want a reference variable targetting the
        # "position" attribute of the "edges" visual.
        self.add_visual(SpriteVisual, position=RefVar('edges', 'position'),
            color=color, texture=get_tex(8), name='nodes')

            
if __name__ == '__main__':
    # create window
    window = show_basic_window(paint_manager=GraphPaintManager, 
                antialiasing=True, constrain_navigation=False)
