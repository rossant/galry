"""Raster plot example."""
import numpy as np
from galry import *

# Total number of spikes.
spikecount = 20000

# Total number of neurons.
n = 100

# Random neuron index for each spike.
neurons = np.random.randint(low=0, high=n, size=spikecount)

# One Poisson spike train with all spikes.
spiketimes = np.cumsum(np.random.exponential(scale=.01, size=spikecount))

# Neurons colors.
colors = np.random.rand(n, 3)

# New figure.
figure(constrain_navigation=True)

# We plot the neuron index wrt. spike times, with a | marker and the specified
# color.
plot(spiketimes, neurons, '|', ms = 5., color=colors[neurons, :])

# We specify the y axis limits.
ylim(-1, n)

# We plot the figure.
show()
