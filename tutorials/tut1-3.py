"""Tutorial 1.3: Rasterplot.

In this tutorial, we show how to plot a raster plot using point sprites.
"""

from galry import *
from numpy import *

# Total number of spikes.
spikecount = 20000

# Total number of neurons.
n = 100

# Random neuron index for each spike.
neurons = random.randint(low=0, high=n, size=spikecount)

# One Poisson spike train with all spikes.
spiketimes = cumsum(random.exponential(scale=.01, size=spikecount))

# Neurons colors.
colors = random.rand(n, 3)

# New figure.
figure(constrain_navigation=True)

# We plot the neuron index wrt. spike times, with a | marker and the specified
# color.
plot(spiketimes, neurons, '|', ms = 5., color=colors[neurons, :])

# We specify the y axis limits.
ylim(-1, n)

# We plot the figure.
show()
