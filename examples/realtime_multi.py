"""Real-time example.

This example shows how a real-time visualizer of multiple digital signals can
be written with Galry.

"""
import numpy as np
from galry import *

# initial values
nsamples = 1000
nplots = 10
t = np.tile(np.linspace(-1., 1., nsamples), (nplots, 1))
x = .01 * np.random.randn(nplots, nsamples) + np.linspace(-.75, .75, nplots)[:,np.newaxis]

# this function returns 10*nplots new values at each call
def get_new_data():
    return .01 * np.random.randn(nplots, 10) + np.linspace(-.75, .75, nplots)[:,np.newaxis]

# this function updates the plot at each call
def anim(fig, _):
    # append new data to the signal
    global x
    x = np.hstack((x[:,10:], get_new_data()))
    
    # create the new 1000*nplots*2 position array with x, y values at each row
    position = np.vstack((t.flatten(), x.flatten())).T
    
    # update the position of the plot
    fig.set_data(position=position)

# plot the signal
plot(t, x)

# animate the plot: anim is called every 25 milliseconds
animate(anim, dt=.025)

# show the figure
show()
