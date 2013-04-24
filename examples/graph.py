"""Display an interactive graph with force-based dynamical layout. Nodes
can be moved with the mouse."""
from galry import *
import numpy.random as rdn
import networkx as nx
from networkx import adjacency_matrix
import itertools

def update(figure, parameter):
    
    x = figure.nodes_positions
    M = figure.M
    
    # figure.forces = -.05 * x#np.dot(M, x)
    
    u = x[:,0] - x[:,0].reshape((-1, 1))
    v = x[:,1] - x[:,1].reshape((-1, 1))
    r = np.sqrt(u ** 2 + v ** 2) ** 3
    # dist = np.sqrt(x[:,0] ** 2 + x[:,1] ** 2)
    
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
    
    c = .1
    
    # damping
    damp = .95
    
    figure.forces = np.empty((len(x), 2))
    figure.forces[:,0] = -c * x[:,0] + a * u1.ravel() + b * u2
    figure.forces[:,1] = -c * x[:,1] + a * v1.ravel() + b * v2
    
    v = damp * (figure.velocities + figure.forces * figure.dt)
    if getattr(figure, 'selected_node', None) is not None:
        v[figure.selected_node] = figure.velocities[figure.selected_node]
    figure.velocities = v
    
    e = (figure.velocities ** 2).sum()
    if e > 2e-3:
        
        figure.nodes_positions += figure.velocities * figure.dt
        figure.set_data(position=figure.nodes_positions, visual='graph_edges')

    if not hasattr(figure, '_viewbox'):
        figure._viewbox = (-10., -10., 10., 10.)
        figure.process_interaction('SetViewbox', figure._viewbox)
        
def node_moved(figure, parameter):
    x0, y0, x, y = parameter
    x0, y0 = figure.get_processor('navigation').get_data_coordinates(x0, y0)
    x, y = figure.get_processor('navigation').get_data_coordinates(x,y)
    p = getattr(figure, 'nodes_positions')
    if getattr(figure, 'selected_node', None) is None:
        r = (p[:,0] - x0) ** 2 + (p[:,1] - y0) ** 2
        figure.selected_node = r.argmin()
    p[figure.selected_node,:] = (x, y)
    figure.set_data(position=p, visual='edges')

def end_moved(figure, parameter):        
    if getattr(figure, 'selected_node', None) is not None:
        figure.selected_node = None
    
        
            
f = figure(antialiasing=True)


n = 100
# we define a random graph with networkx
# g = nx.barabasi_albert_graph(n, 5)

# g = nx.erdos_renyi_graph(n, 0.01)
g=nx.watts_strogatz_graph(n, 3, 0.5)
# g=nx.barabasi_albert_graph(n,5)
# g=nx.random_lobster(n, 0.9, 0.9)

# edges = itertools.combinations(g.subgraph(range(20)), 2)
# g.add_edges_from(edges)

f.M = adjacency_matrix(g)
f.Ms = f.M.sum(axis=1)

# get the array with the positions of all nodes
# positions = np.vstack([pos[i] for i in xrange(len(pos))]) - .5
positions = rdn.randn(n, 2) * .2

# get the array with the positions of all edges.
edges = np.vstack(g.edges()).ravel()

# random colors for the nodes
color = np.random.rand(len(positions), 4)
color[:,-1] = 1

coledges = (1., 1., 1., .25)

size = np.random.randint(low=50, high=200, size=n)

graph(position=positions, edges=edges, color=color, edges_color=coledges,
    node_size=size, name='graph')

    
f.edges = edges
f.nodes_positions = positions
f.velocities = np.zeros((len(positions), 2))
f.forces = np.zeros((len(positions), 2))
f.dt = .02



action('MiddleClickMove', 'NodeMoved',
       param_getter=lambda p: p["mouse_press_position"] + p["mouse_position"])
action('LeftClickMove', 'NodeMoved',
       key_modifier='Control',
       param_getter=lambda p: p["mouse_press_position"] + p["mouse_position"])

event('NodeMoved', node_moved)
event(None, end_moved)

animate(update, dt=f.dt)

print "Move nodes with middle-click + move"

show()