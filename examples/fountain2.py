"""Particle system example bis with user interaction."""
from galry import *
import pylab as plt
import numpy as np
import numpy.random as rdn
import os
import time
import timeit
from fountain import ParticleVisual

class Particle2Visual(ParticleVisual):
    def get_position_update_code(self):
        return """
        // update position
        position.x += (velocities.x + v.x) * tloc;
        position.y += (velocities.y + v.y) * tloc - 0.5 * g * tloc * tloc;
        """
        
    def initialize(self, v=None, **kwargs):
        if v is None:
            v = (0., 0.)
        self.base_fountain(**kwargs)
        self.add_uniform("v", vartype="float", ndim=2, data=v)
        


def update(figure, parameter):
    t = parameter[0]
    v = getattr(figure, 'v', (0., 0.))
    figure.set_data(t=t, v=v)

def change_v(figure, parameter):
    figure.v = parameter
    


figure(constrain_navigation=True)


# number of particles
n = 20000

# initial positions
positions = .02 * rdn.randn(n, 2)

# initial velocities
velocities = .2 * rdn.rand(n, 2)
v = (0., 0.)

# transparency
alpha = .5 * rdn.rand(n)

# color
color = (0.70,0.75,.98,1.)

# random delays
delays = 10 * rdn.rand(n)

# create the dataset
visual(Particle2Visual, 
    initial_positions=positions,
    velocities=velocities,
    v=v,
    alpha=alpha,
    color=color,
    delays=delays
    )

action('Move', change_v,
       param_getter=lambda p: 
            (2 * p["mouse_position"][0],
             2 * p["mouse_position"][1]))


animate(update, dt=.02)

show()

