from visual import Visual
import numpy as np

class FrameBufferVisual(Visual):
    def initialize(self, shape=None):
        self.add_texture('fbotex', ncomponents=3, ndim=2, shape=shape,
            data=np.zeros((shape[0], shape[1], 3)))
        self.add_framebuffer('fbo', texture='fbotex')
        
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
        self.add_fragment_main("""
        out_color = texture2D(fbotex, vtex_coords);
        """)
        
