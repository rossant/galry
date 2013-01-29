"""Dash line example with binary texture."""

from galry import *
import numpy as np

# sin(x) function
x = np.linspace(-10., 10., 1000)
y = np.sin(x)

# to make dashes, we use a 1D texture with B&W colors...
color = np.array(get_color(['k', 'w']))

# and a lookup colormap index with alternating 0 and 1
index = np.zeros(len(x))
index[::2] = 1

# we then plot the graph and specify the texture and the colormap
plot(x=x, y=y, color_array_index=index, color=color,)

show()