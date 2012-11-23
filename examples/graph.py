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
        
        # we define a random graph with networkx
        g = nx.barabasi_albert_graph(100, 3)
        
        # we compute the layout, ie the positions of the nodes, with
        # networkx, on the GPU. This might be a bottleneck when dealing with
        # large graphs, so one should consider doing that on the GPU is
        # possible
        pos = nx.spring_layout(g)
        
        # get the array with the positions of all nodes
        positions = np.vstack([pos[i] for i in xrange(len(pos))]) - .5
        
        # get the array with the positions of all edges.
        # NOTE: we're wasting a lot of memory and it should be better to use
        # indexed arrays. However those are not yet implemented in galry
        # this is on the TODO list...
        edges = np.vstack(g.edges()).ravel()
        # posedges = positions[edges,:]
        
        # random colors for the nodes
        color = np.random.rand(len(positions), 3)
        
        # add dataset with the nodes
        self.add_visual(SpriteVisual, position=positions, color=color,
            texture=get_tex(16))

        # add dataset with the edges
        # coledges = np.hstack((color[edges,:], .5 * np.ones((len(edges), 1))))
        coledges = (1., 1., 1., .1)
        # self.add_visual(PlotVisual, position=posedges,
            # primitive_type='LINES', color=coledges)
        self.add_visual(PlotVisual, position=positions,
            primitive_type='LINES', color=coledges, index=edges)
            
if __name__ == '__main__':
    # create window
    window = show_basic_window(paint_manager=GraphPaintManager, 
                antialiasing=True, constrain_navigation=False)
