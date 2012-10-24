from galry import *
import numpy as np
import numpy.random as rdn
import pylab as plt
import os
import time

# Vertex shader
VS = """
%AUTODECLARATIONS%

void main()
{
    // compute local time
    float tloc = t - delays;
    if (tloc < 0)
        return;
    tloc = mod(tloc, tmax);
    if (tloc > tlocmax)
        return;

    // update position
    vec4 position;
    position.x = initial_positions.x + (velocities.x + v.x) * tloc;
    position.y = initial_positions.y + (velocities.y + v.y) * tloc - 0.5 * g * tloc * tloc;

    // position with or without interactive transformation
    if (!is_static)
        gl_Position = gl_ModelViewProjectionMatrix * position;
    else
        gl_Position = position;
        
    // pass the color and point size to the fragment shader
    gl_FrontColor = gl_Color;
    gl_FrontColor.w = alpha;
    gl_PointSize = point_size;
}
"""

# Fragment shader
FS = """
uniform sampler2D tex_sampler0;
void main()
{
    // display colored texture (sprite)
    gl_FragColor = texture2D(tex_sampler0, gl_PointCoord) * gl_Color;
}
"""

# load texture
path = os.path.dirname(os.path.realpath(__file__))
particle = plt.imread(os.path.join(path, "images/particle.png"))

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
        
        # transparency
        alpha = .2 * rdn.rand(n)
        
        # color
        color = (0.65,0.70,1.)
        
        # random delays
        delays = 10 * rdn.rand(n)
        
        # particle texture size
        size = float(max(particle.shape))

        self.v = (0., 0.)
        
        # create the dataset
        self.create_dataset(n, primitive_type=PrimitiveType.Points,
                                vertex_shader=VS,
                                fragment_shader=FS,
                                point_size=size,
                                color=color,
                                t=0., g=g, tmax=tmax, tlocmax=tlocmax,
                                v=self.v,
                                )
        # add the different data buffers
        self.add_buffer("initial_positions", positions)
        self.add_buffer("velocities", velocities)
        self.add_buffer("delays", delays)
        self.add_buffer("alpha", alpha)
        
        # add particle texture
        self.add_texture("texture", particle)
        
    def change_velocities(self, v):
        # change the velocity direction
        self.t = time.clock() - self.t0
        self.v = v
        self.update_uniform_values(t=self.t, v=self.v)
        
    def update(self):
        # update the t uniform value
        self.t = time.clock() - self.t0
        self.update_uniform_values(t=self.t, v=self.v)
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
