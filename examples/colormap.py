from galry import *
import numpy as np
from pylab import imread

class ColormapVisual(Visual):
    def initialize(self, colormap):
        
        ncolors = colormap.shape[0]
        ncomponents = colormap.shape[1]
        
        colormap = colormap.reshape((1, ncolors, ncomponents))
        
        position = np.random.randn(1000, 2) * .2
        self.size = position.shape[0]
        
        color_indices = np.random.randint(low=0, high=ncolors, size=self.size)
        
        self.primitive_type = 'POINTS'
        
        dx = 1. / ncolors
        offset = dx / 2.
        
        self.add_attribute('position', ndim=2, data=position)
        
        
        self.add_texture('colormap', ncomponents=ncomponents, ndim=1, data=colormap)
        self.add_attribute('index', ndim=1, vartype='int', data=color_indices)
        self.add_varying('vindex', vartype='int', ndim=1)
        
        self.add_vertex_main("""
        gl_PointSize = 10.;
        vindex = index;
        """)
        
        self.add_fragment_main("""
        vec4 color = texture1D(colormap, %.1f + vindex * %.1f);
        out_color = color;
        """ % (offset, dx))
        

class PM(PaintManager):
    def initialize(self):
        colormap = np.ones((3, 4))
        colormap[0,:3] = (1,0,0)
        colormap[1,:3] = (0,1,0)
        colormap[2,:3] = (0,0,1)
        self.add_visual(ColormapVisual, colormap=colormap)
    
if __name__ == '__main__':
    show_basic_window(paint_manager=PM)
    