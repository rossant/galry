from galry import *
import pylab as plt
import numpy as np
import numpy.random as rdn
import os
import time

class ParticleTemplate(DefaultTemplate):
    def initialize(self,  **kwargs):

        # load texture
        path = os.path.dirname(os.path.realpath(__file__))
        particle = plt.imread(os.path.join(path, "images/particle.png"))
        
        size = float(max(particle.shape))
        
        # create the dataset
        self.add_uniform("point_size", vartype="float", ndim=1, data=size)
        self.add_uniform("t", vartype="float", ndim=1, data=0.)
        self.add_uniform("v", vartype="float", ndim=2, data=(0., 0.))
        self.add_uniform("g", vartype="float", ndim=1, data=0.)
        self.add_uniform("tmax", vartype="float", ndim=1)
        self.add_uniform("tlocmax", vartype="float", ndim=1)
        
        self.add_uniform("color", vartype="float", ndim=4)
        self.add_varying("varying_color", vartype="float", ndim=4)
        
        # add the different data buffers
        self.add_attribute("initial_positions", vartype="float", ndim=2)
        self.add_attribute("velocities", vartype="float", ndim=2)
        self.add_attribute("delays", vartype="float", ndim=1)
        self.add_attribute("alpha", vartype="float", ndim=1)
        
        # add particle texture
        self.add_texture("tex_sampler", size=particle.shape[:2],
            ncomponents=particle.shape[2], ndim=2, data=particle)
            
        self.add_vertex_main(
"""
    // compute local time
    float tloc = t - delays;
    if (tloc < 0)
        return;
    tloc = mod(tloc, tmax);
    if (tloc > tlocmax)
        return;

    // update position
    vec4 position = vec4(0,0,0,1);
    position.x = initial_positions.x + (velocities.x + v.x) * tloc;
    position.y = initial_positions.y + (velocities.y + v.y) * tloc - 0.5 * g * tloc * tloc;
    
    // pass the color and point size to the fragment shader
    varying_color = color;
    varying_color.w = alpha;
    
    gl_PointSize = point_size;
""")    


        self.add_fragment_main(
"""
    out_color = texture(tex_sampler, gl_PointCoord) * varying_color;
""")
        
        super(ParticleTemplate, self).initialize(**kwargs)

class ParticlePaintManager(PaintManager):
    def initialize(self):
        # time variables
        self.t = 0.0
        self.t0 = time.clock()
        self.dt = .01
        tmax = 5.
        tlocmax = 2.
        
        # number of particles
        n = 200000
        
        # gravity acceleration
        g = 4.
        
        # initial positions
        positions = .02 * rdn.randn(n, 2)
        
        # initial velocities
        velocities = .2 * rdn.randn(n, 2)
        
        self.v = (0., 0.)
        
        # transparency
        alpha = .2 * rdn.rand(n)
        
        # color
        color = (0.70,0.75,.98,1.)
        
        # random delays
        delays = 10 * rdn.rand(n)
        
        # create the dataset
        self.create_dataset(ParticleTemplate, size=n)
        self.set_data(t=self.t, tmax=tmax, tlocmax=tlocmax, g=g,
            initial_positions=positions,
            velocities=velocities, alpha=alpha, color=color, v=self.v,
            delays=delays)
        
    def change_velocities(self, v):
        # change the velocity direction
        self.t = time.clock() - self.t0
        self.v = v
        self.set_data(t=self.t, v=self.v)
        
    def update(self):
        # update the t uniform value
        self.t = time.clock() - self.t0
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
        
        
        
        
class ParticlePlot(GalryWidget):
    def initialize(self):
        # set custom paint manager
        self.set_companion_classes(paint_manager=ParticlePaintManager,
                                   interaction_manager=ParticleInteractionManager)
        self.set_bindings(ParticleBindings)
    
    def initialized(self):
        # start simulation after initialization completes
        self.timer = QtCore.QTimer()
        self.timer.setInterval(self.paint_manager.dt * 1000)
        self.timer.timeout.connect(self.paint_manager.update)
        self.timer.start()
        
    def showEvent(self, e):
        # start simulation when showing window
        self.timer.start()
        
    def hideEvent(self, e):
        # stop simulation when hiding window
        self.timer.stop()

if __name__ == '__main__':
    window = show_basic_window(widget_class=ParticlePlot)
