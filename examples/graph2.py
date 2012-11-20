from galry import *
import numpy.random as rdn
import networkx as nx
from networkx import adjacency_matrix

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
        g = nx.barabasi_albert_graph(100, 5)
        self.M = adjacency_matrix(g)
        self.Ms = self.M.sum(axis=1)
        
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
        posedges = positions[edges,:]
        
        # random colors for the nodes
        color = np.random.rand(len(positions), 4)
        color[:,-1] = 1
        
        # add dataset with the nodes
        self.ds_nodes = self.create_dataset(SpriteTemplate, position=positions,
            color=color, texture=get_tex(16))

        # add dataset with the edges
        coledges = color.copy()[edges,:]# np.hstack((color[edges,:], .5 * np.ones((len(edges), 1))))
        coledges[:,-1] = .25
        self.ds_edges = self.create_dataset(PlotTemplate, position=posedges,
            primitive_type=PrimitiveType.Lines, color=coledges)

        self.edges = edges
        self.nodes_positions = positions
        self.edges_positions = posedges
        self.velocities = np.zeros((len(positions), 2))
        self.forces = np.zeros((len(positions), 2))
        self.dt = .02
        
    
    def update_callback(self):

        
        x = self.nodes_positions
        M = self.M
        
        # self.forces = -.05 * x#np.dot(M, x)
        
        u = x[:,0] - x[:,0].reshape((-1, 1))
        v = x[:,1] - x[:,1].reshape((-1, 1))
        r = np.sqrt(u ** 2 + v ** 2) ** 3
        
        
        # ind = r==0.
        r[r<.01] = np.inf
        
        u1 = u / r
        # u[ind] = 0
        u1 = u1.sum(axis=1)
        
        v1 = v / r
        # v[ind] = 0
        v1 = v1.sum(axis=1)
        
        r[r==np.inf] = 0
        
        u *= M
        v *= M
        
        u2 = u * r
        v2 = v * r
        
        u2 = u2.sum(axis=1)
        v2 = v2.sum(axis=1)
        
        a = -.5
        b = .5
        self.forces = np.empty((len(x), 2))
        self.forces[:,0] = a * u1.ravel() + b * u2
        self.forces[:,1] = a * v1.ravel() + b * v2
        
        v = .9 * (self.velocities + self.forces * self.dt)
        if self.interaction_manager.selected_node is not None:
            v[self.interaction_manager.selected_node] = self.velocities[self.interaction_manager.selected_node]
        self.velocities = v
        
        e = (self.velocities ** 2).sum()
        if e > 2e-3:
            
            self.nodes_positions += self.velocities * self.dt
            self.update_pos(self.nodes_positions)
    
    def update_pos(self, pos):
        self.nodes_positions = pos
        self.set_data(dataset=self.ds_nodes, position=pos)
        self.set_data(dataset=self.ds_edges, position=pos[self.edges,:])
        
    
class GraphInteractionManager(InteractionManager):
    
    
    selected_node = None
    def node_moved(self, pos):
        x0, y0, x, y = pos
        x0, y0 = self.get_data_coordinates(x0, y0)
        x, y = self.get_data_coordinates(x,y)
        p = self.paint_manager.nodes_positions
        if self.selected_node is None:
            r = (p[:,0] - x0) ** 2 + (p[:,1] - y0) ** 2
            self.selected_node = r.argmin()
        p[self.selected_node,:] = (x, y)
        self.paint_manager.update_pos(p)
    
    def process_none_event(self):
        super(GraphInteractionManager, self).process_none_event()
        if self.selected_node is not None:
            self.selected_node = None
    
    def process_custom_event(self, event, parameter):
        if event == "NodeMoved":
            self.node_moved(parameter)
    
    
class GraphBinding(DefaultBindingSet):
    def extend(self):
        self.set(UserActions.LeftButtonMouseMoveAction,
            "NodeMoved", param_getter=lambda p: p["mouse_press_position"] + p["mouse_position"])
        
            
if __name__ == '__main__':
    # create window
    window = show_basic_window(
        bindings=GraphBinding,
        paint_manager=GraphPaintManager, 
        interaction_manager=GraphInteractionManager,
        antialiasing=True, constrain_navigation=False,
        display_fps=True,
        update_interval=.02)
