from galry import *
import pylab as plt
import numpy as np
import numpy.random as rdn
import time
import timeit
import os

# f = 2.




class ParticleVisual(Visual):
    def get_position_update_code(self):
        return """
        // update position
        position.x += velocities.x * tloc;
        position.y += velocities.y * tloc - 0.5 * g * tloc * tloc;
        """
        
    def get_color_update_code(self):
        return """
        // pass the color and point size to the fragment shader
        varying_color = color;
        varying_color.w = .20;
        """
    
    def base_fountain(self, initial_positions=None,
        velocities=None, color=None, delays=None, 
        ):
        
        self.size = initial_positions.shape[0]
        self.primitive_type = 'POINTS'
        # load texture
        path = os.path.dirname(os.path.realpath(__file__))
        particle = plt.imread(os.path.join(path, "../examples/images/particle.png"))
        
        size = float(max(particle.shape))
        
        # create the dataset
        self.add_uniform("point_size", vartype="float", ndim=1, data=size)
        self.add_uniform("t", vartype="float", ndim=1, data=0.)
        self.add_uniform("color", vartype="float", ndim=4, data=color)
        
        # add the different data buffers
        self.add_attribute("initial_positions", vartype="float", ndim=2, data=initial_positions)
        self.add_attribute("velocities", vartype="float", ndim=2, data=velocities)
        self.add_attribute("delays", vartype="float", ndim=1, data=delays)
        
        self.add_varying("varying_color", vartype="float", ndim=4)
        
        # add particle texture
        self.add_texture("tex", size=particle.shape[:2],
            ncomponents=particle.shape[2], ndim=2, data=particle)
            
        vs = """
        // compute local time
        const float tmax = 5.;
        const float tlocmax = 2.;
        const float g = %G_CONSTANT%;
        
        // Local time.
        float tloc = mod(t - delays, tmax);
        
        vec2 position = initial_positions;
        
        if ((tloc >= 0) && (tloc <= tlocmax))
        {
            // position update
            %POSITION_UPDATE%
            
            %COLOR_UPDATE%
        }
        else
        {
            varying_color = vec4(0., 0., 0., 0.);
        }
        
        gl_PointSize = point_size;
        """
            
        vs = vs.replace('%POSITION_UPDATE%', self.get_position_update_code())
        vs = vs.replace('%COLOR_UPDATE%', self.get_color_update_code())
        vs = vs.replace('%G_CONSTANT%', '3.')
            
        self.add_vertex_main(vs)    
        
        self.add_fragment_main(
        """
            vec4 col = texture2D(tex, gl_PointCoord) * varying_color;
            out_color = col;
        """)

    def initialize(self, **kwargs):
        self.base_fountain(**kwargs)

class MyVisual(Visual):
    def initialize(self, shape=None):
        if shape is None:
            shape = (600, 600)
        
        self.add_texture('singletex', ncomponents=3, ndim=2,
            shape=shape,
            data=np.zeros((shape[0], shape[1], 3))
            )
            
        self.add_texture('fulltex', ncomponents=3, ndim=2,
            shape=shape,
            data=np.zeros((shape[0], shape[1], 3))
            )
        
        points = (-1, -1, 1, 1)
        x0, y0, x1, y1 = points
        x0, x1 = min(x0, x1), max(x0, x1)
        y0, y1 = min(y0, y1), max(y0, y1)
        
        position = np.zeros((4,2))
        position[0,:] = (x0, y0)
        position[1,:] = (x1, y0)
        position[2,:] = (x0, y1)
        position[3,:] = (x1, y1)
        
        tex_coords = np.zeros((4,2))
        tex_coords[0,:] = (0, 0)
        tex_coords[1,:] = (1, 0)
        tex_coords[2,:] = (0, 1)
        tex_coords[3,:] = (1, 1)
    
        self.size = 4
        self.primitive_type = 'TRIANGLE_STRIP'
        
        # texture coordinates
        self.add_attribute("tex_coords", vartype="float", ndim=2,
            data=tex_coords)
        self.add_varying("vtex_coords", vartype="float", ndim=2)
        
        self.add_attribute("position", vartype="float", ndim=2, data=position)
        self.add_vertex_main("""vtex_coords = tex_coords;""")
        
        FS = """
        vec4 out0 = texture2D(singletex, vtex_coords);
        vec4 out1 = texture2D(fulltex, vtex_coords);
        float a = .05;
        out_color = a * out0 + (1-a) * out1;
        if (out_color.x + out_color.y + out_color.z < .04)
            out_color = vec4(0, 0, 0, 0);
        """
        self.add_fragment_main(FS)
            
def update(figure, parameter):
    t = parameter[0]
    
    figure.set_data(t=t, visual='fountain')
    
    figure.copy_texture(RefVar('singlefbo', 'fbotex0'), 'singletex', visual='myvisual')
    figure.copy_texture(RefVar('fullfbo', 'fbotex0'), 'fulltex', visual='myvisual')

if __name__ == '__main__':
    
        
    # number of particles
    n = 50000

    # initial positions
    positions = .02 * rdn.randn(n, 2)

    # initial velocities
    velocities = np.zeros((n, 2))
    v = 1.5 + .5 * rdn.rand(n)
    angles = .1 * rdn.randn(n) + np.pi / 2
    velocities[:,0] = v * np.cos(angles)
    velocities[:,1] = v * np.sin(angles)

    # color
    color = (0.60,0.65,.98,1.)

    # random delays
    delays = 10 * rdn.rand(n)
    
    # # create the visual
    visual(ParticleVisual, 
        initial_positions=positions,
        velocities=velocities,
        color=color,
        delays=delays,
        is_static=True,
        name='fountain',
        )

    framebuffer(name='singlefbo', display=False)
    framebuffer(name='fullfbo', is_static=True)
        
    # # FBO #0 => #1
    visual(MyVisual, name='myvisual', framebuffer=1,
        is_static=True,)
    
    animate(update, dt=.01)

    show()

