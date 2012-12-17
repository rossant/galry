import numpy as np
from galry import *

class DepthVisual(Visual):
    def initialize(self, position, color):
        self.size = position.shape[0]
        self.add_attribute('position', ndim=3, data=position)
        self.add_attribute('color', ndim=4, data=color)
        self.add_varying('vcolor', ndim=4)
        self.primitive_type = 'POINTS'
        self.depth_enabled = True
        self.add_vertex_main("""
        gl_PointSize = 100.;
        vcolor = color;
        """)
        self.add_fragment_main("""
        out_color = vcolor;
        """)

figure(activate3D=True)

position = np.zeros((10, 3))
position[:,0] = position[:,1] = np.linspace(-.5, .5, 10)
position[:,2] = np.linspace(0., 1., 10)

color = np.tile(np.linspace(0., 1., 10).reshape((-1, 1)), (1, 4))
color[:,-1] = 0.5
visual(DepthVisual, position, color)

show()

