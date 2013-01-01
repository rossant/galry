from visual import Visual
import numpy as np

class FrameBufferVisual(Visual):
    def initialize(self, shape=None, ntextures=1, coeffs=None, display=True):
        if shape is None:
            shape = (600, 600)
        
        for i in xrange(ntextures):
            self.add_texture('fbotex%d' % i, ncomponents=3, ndim=2, shape=shape,
                data=np.zeros((shape[0], shape[1], 3)))
        # self.add_texture('fbotex2', ncomponents=3, ndim=2, shape=shape,
            # data=np.zeros((shape[0], shape[1], 3)))
        # self.add_framebuffer('fbo', texture=['fbotex', 'fbotex2'])
        self.add_framebuffer('fbo', texture=['fbotex%d' % i for i in xrange(ntextures)])
        
        if not display:
            self.add_attribute('position', ndim=2)#, data=np.zeros((1, 2)))
            self.size = 0
            return
        
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
        
        if coeffs is None:
            self.add_fragment_main("""
            out_color = texture2D(fbotex0, vtex_coords);
            """)
        else:
            FS = ""
            for i in xrange(ntextures):
                FS += """
                vec4 out%d = texture2D(fbotex%d, vtex_coords);
                """ % (i, i)
            FS += "out_color = " + " + ".join(["%.5f * out%d" % (coeffs[i], i) for i in xrange(ntextures)]) + ";"
            self.add_fragment_main(FS)
            
