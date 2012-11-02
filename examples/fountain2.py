from galry import *
import pylab as plt
import numpy as np
import numpy.random as rdn
import os
import time
import timeit
from fountain import ParticleTemplate, ParticlePaintManager, ParticlePlot

class Particle2Template(ParticleTemplate):
    def get_position_update_code(self):
        return """
        // update position
        position.x += (velocities.x + v.x) * tloc;
        position.y += (velocities.y + v.y) * tloc - 0.5 * g * tloc * tloc;
        """
        
    def initialize(self,  **kwargs):
        self.base_fountain()
        self.add_uniform("v", vartype="float", ndim=2, data=(0., 0.))
        self.initialize_default(**kwargs)
        
class Particle2PaintManager(PaintManager):
    def initialize(self):
        # time variables
        self.t = 0.0
        self.t0 = timeit.default_timer()
        self.freq = 50.
        
        # number of particles
        n = 20000
        
        # initial positions
        positions = .02 * rdn.randn(n, 2)
        
        # initial velocities
        velocities = .2 * rdn.rand(n, 2)
        self.v = (0., 0.)
        
        # transparency
        alpha = .5 * rdn.rand(n)
        
        # color
        color = (0.70,0.75,.98,1.)
        
        # random delays
        delays = 10 * rdn.rand(n)
        
        # create the dataset
        self.create_dataset(Particle2Template, 
            t=self.t, 
            initial_positions=positions,
            velocities=velocities,
            v=self.v,
            alpha=alpha,
            color=color,
            delays=delays
            )
        
    def change_velocities(self, v):
        # change the velocity direction
        self.t = timeit.default_timer() - self.t0
        self.v = v
        self.set_data(t=self.t, v=self.v)
        
    def update(self):
        # update the t uniform value
        self.t = timeit.default_timer() - self.t0
        self.set_data(t=self.t, v=self.v)
        self.updateGL()
        
class ParticleInteractionManager(InteractionManager):
    def process_extended_event(self, event, parameter):
        # process our custom event
        if event == ParticleEvents.ChangeVelocitiesEvent:
            self.paint_manager.change_velocities(parameter)
        
ParticleEvents = enum("ChangeVelocitiesEvent")

class ParticleBindings(ActionEventBindingSet):
    def initialize(self):
        # we link the mouse move action to the change velocities event
        self.set(UserActions.MouseMoveAction, ParticleEvents.ChangeVelocitiesEvent,
                 param_getter=lambda p: 
                    (2 * p["mouse_position"][0],
                     2 * p["mouse_position"][1]))
        
class Particle2Plot(ParticlePlot):
    def initialize(self):
        # set custom paint manager
        self.set_companion_classes(paint_manager=Particle2PaintManager,
                                   interaction_manager=ParticleInteractionManager)
        self.set_bindings(ParticleBindings)

if __name__ == '__main__':
    window = show_basic_window(widget_class=Particle2Plot)
