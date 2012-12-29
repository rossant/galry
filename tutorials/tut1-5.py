"""Tutorial 1.5: Graphs.

In this tutorial we show how to plot graphs.

"""

from galry import *
from numpy import *

# We use networkx because it provides convenient functions to create and
# manipulate graphs, but this library is not required by Galry.
import networkx as nx

# We create a complete graph.      
g = nx.complete_graph(50)

# We compute a circular layout and get an array with the positions
# of all nodes.
pos = nx.circular_layout(g)
position = np.vstack([pos[i] for i in xrange(len(pos))]) - .5

# We retrieve the edges as an array where each line contains the two node
# indices of an edge, the indices referring to the `position` array.
edges = np.vstack(g.edges())

# We define random colors for all nodes, with an alpha channel to 1.
color = np.random.rand(len(position), 4)
color[:,-1] = 1

# We define the edges colors: the color in line i is the color of all
# edges linking node i to any other node. If an edge has two different colors
# at its two ends, then its color will be a gradient between the two colors.
# Here, we simply use the same color for nodes and edges, but with an
# alpha channel at 0.25.
edges_color = color.copy()
edges_color[:,-1] = .25

figure(constrain_ratio=True)

# We plot the graph.
graph(position=position, edges=edges, color=color, edges_color=edges_color)

show()
