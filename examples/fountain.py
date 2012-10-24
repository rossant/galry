from galry import *
import pylab as plt
import numpy as np
import numpy.random as rdn
import os

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
    position.x = initial_positions.x + velocities.x * tloc;
    position.y = initial_positions.y + velocities.y * tloc - 0.5 * g * tloc * tloc;

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
        velocities = np.zeros((n, 2))
        v = 2 + .5 * rdn.rand(n)
        angles = .1 * rdn.randn(n) + np.pi / 2
        velocities[:,0] = v * np.cos(angles)
        velocities[:,1] = v * np.sin(angles)
        
        # transparency
        alpha = .2 * rdn.rand(n)
        
        # color
        color = (0.70,0.75,.98)
        
        # random delays
        delays = 10 * rdn.rand(n)
        
        # particle texture size
        size = float(max(particle.shape))
        
        # create the dataset
        self.create_dataset(n, primitive_type=PrimitiveType.Points,
                                vertex_shader=VS,
                                fragment_shader=FS,
                                point_size=size,
                                color=color,
                                t=0., g=g, tmax=tmax, tlocmax=tlocmax,
                                )
        # add the different data buffers
        self.add_buffer("initial_positions", positions)
        self.add_buffer("velocities", velocities)
        self.add_buffer("delays", delays)
        self.add_buffer("alpha", alpha)
        
        # add particle texture
        self.add_texture("texture", particle)
        
    def update(self):
        # update the t uniform value
        self.update_uniform_values(t=self.t)
        self.t += self.dt
        self.updateGL()
        
class ParticlePlot(GalryWidget):
    def initialize(self):
        # set custom paint manager
        self.set_companion_classes(paint_manager=ParticlePaintManager)
    
    def initialized(self):
        # start simulation after initialization completes
        self.timer = QtCore.QTimer()
        self.timer.setInterval(self.paint_manager.dt * 1000)
        self.timer.timeout.connect(self.paint_manager.update)
        self.timer.start()
        
    # i = 0
    # def updateGL(self):
        # super(ParticlePlot, self).updateGL()
        # file = "screens/image%05d.png" % self.i
        # self.save_image(file)
        # self.i += 1
        
    def showEvent(self, e):
        # start simulation when showing window
        self.timer.start()
        
    def hideEvent(self, e):
        # stop simulation when hiding window
        self.timer.stop()

if __name__ == '__main__':
    window = show_basic_window(widget_class=ParticlePlot)
