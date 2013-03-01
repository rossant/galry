"""Real-time example.

This example shows how a real-time visualizer of digital signals can
be written with Galry.

"""
import numpy as np
from galry import *

# initial values
t = np.linspace(-1., 1., 1000)
x = .1 * np.random.randn(1000)

# this function returns 10 new values at each call
def get_new_data():
    return .1 * np.random.randn(10)

# this function updates the plot at each call
def anim(fig, _):
    # append new data to the signal
    global x
    x = np.hstack((x[10:], get_new_data()))
    
    # create the new 1000x2 position array with x, y values at each row
    position = np.vstack((t, x)).T
    
    # update the position of the plot
    fig.set_data(position=position)

# plot the signal
plot(t, x)

# animate the plot: anim is called every 25 milliseconds
animate(anim, dt=.025)

# show the figure
show()
