from galry import *
import numpy.random as rdn
import networkx as nx
from networkx import adjacency_matrix
import itertools

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
        
        n = 200
        # we define a random graph with networkx
        # g = nx.barabasi_albert_graph(n, 5)
        
        # g = nx.erdos_renyi_graph(n, 0.01)
        g=nx.watts_strogatz_graph(n, 3, 0.5)
        # g=nx.barabasi_albert_graph(n,5)
        # g=nx.random_lobster(n, 0.9, 0.9)
        
        # edges = itertools.combinations(g.subgraph(range(20)), 2)
        # g.add_edges_from(edges)
        
        self.M = adjacency_matrix(g)
        self.Ms = self.M.sum(axis=1)
        
        # get the array with the positions of all nodes
        # positions = np.vstack([pos[i] for i in xrange(len(pos))]) - .5
        positions = rdn.randn(n, 2) * .2
        
        # get the array with the positions of all edges.
        edges = np.vstack(g.edges()).ravel()
        
        # random colors for the nodes
        color = np.random.rand(len(positions), 4)
        color[:,-1] = 1
        
        coledges = (1., 1., 1., .1)
        
        self.add_visual(PlotVisual, position=positions,
            primitive_type='LINES', color=coledges, index=edges, name='edges')
        
        # add dataset with the nodes
        self.add_visual(SpriteVisual, position=RefVar('edges', 'position'),
            color=color, texture=get_tex(16), name='nodes')

        self.edges = edges
        self.nodes_positions = positions
        # self.edges_positions = posedges
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
        r[r<.01] = .01
        
        u1 = u / r
        # u[ind] = 0
        u1 = u1.sum(axis=1)
        
        v1 = v / r
        # v[ind] = 0
        v1 = v1.sum(axis=1)
        
        r[r>10] = 10
        
        u *= M
        v *= M
        
        u2 = u * r
        v2 = v * r
        
        u2 = u2.sum(axis=1)
        v2 = v2.sum(axis=1)
        
        # repulsion (coulomb)
        a = -.5
        
        # attraction (spring)
        b = 5.
        
        # damping
        damp = .99
        
        self.forces = np.empty((len(x), 2))
        self.forces[:,0] = a * u1.ravel() + b * u2
        self.forces[:,1] = a * v1.ravel() + b * v2
        
        v = damp * (self.velocities + self.forces * self.dt)
        if self.interaction_manager.selected_node is not None:
            v[self.interaction_manager.selected_node] = self.velocities[self.interaction_manager.selected_node]
        self.velocities = v
        
        e = (self.velocities ** 2).sum()
        if e > 2e-3:
            
            self.nodes_positions += self.velocities * self.dt
            self.update_pos(self.nodes_positions)
    
    def update_pos(self, pos):
        self.nodes_positions = pos
        # self.set_data(position=pos, visual='nodes')
        self.set_data(position=pos, visual='edges')
        
    
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
        self.set(UserActions.MiddleButtonMouseMoveAction, "NodeMoved",
            param_getter=lambda p: p["mouse_press_position"] + p["mouse_position"])
        
        self.set(UserActions.LeftButtonMouseMoveAction, "NodeMoved",
            key_modifier=QtCore.Qt.Key_Control,
            param_getter=lambda p: p["mouse_press_position"] + p["mouse_position"])
        
            
if __name__ == '__main__':
    # create window
    window = show_basic_window(
        bindings=GraphBinding,
        paint_manager=GraphPaintManager, 
        interaction_manager=GraphInteractionManager,
        antialiasing=True, constrain_navigation=False,
        display_fps=True,
        update_interval=.01
        )
