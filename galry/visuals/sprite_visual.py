import numpy as np
from visual import Visual
    
class SpriteVisual(Visual):
    """Template displaying one texture in multiple positions with
    different colors."""
    
    def initialize(self, texture=None, position=None, color=None):
        texsize = float(max(texture.shape[:2]))
        shape = (texsize, texsize)        
        ncomponents = texture.shape[2]
        self.size = position.shape[0]
        self.primitive_type = 'POINTS'
        
        # default color
        if color is None:
            color = self.default_color
        
        # handle the case where there is a single color given as a list of
        # RGB components instead of a tuple
        if type(color) is list:
            if color and (type(color[0]) != tuple) and (3 <= len(color) <= 4):
                color = tuple(color)
            else:
                color = np.array(color)
        if isinstance(color, np.ndarray):
            colors_ndim = color.shape[1]
            # one color per point
            single_color = False
        elif type(color) is tuple:
            single_color = True
            colors_ndim = len(color)
        # single color case: no need for a color buffer, just use default color
        if single_color:
            self.add_uniform("color", ndim=colors_ndim, data=color)
            if colors_ndim == 3:
                self.add_fragment_main("""
            out_color = texture(tex_sampler, gl_PointCoord) * vec4(color, 1.0);
                """)
            elif colors_ndim == 4:
                self.add_fragment_main("""
            out_color = texture(tex_sampler, gl_PointCoord) * color;
                """)
        # multiple colors case: color attribute
        else:
            self.add_attribute("color", ndim=colors_ndim, data=color)
            self.add_varying("varying_color", vartype="float", ndim=colors_ndim)
            
            self.add_vertex_main("""
            varying_color = color;
            """)
            
            if colors_ndim == 3:
                self.add_fragment_main("""
            out_color = texture(tex_sampler, gl_PointCoord) * vec4(varying_color, 1.0);
                """)
            elif colors_ndim == 4:
                self.add_fragment_main("""
            out_color = texture(tex_sampler, gl_PointCoord) * varying_color;
                """)
        
        # add variables
        self.add_attribute("position", vartype="float", ndim=2, data=position)
        self.add_texture("tex_sampler", size=shape, ndim=2,
            ncomponents=ncomponents)
        self.add_compound("texture", fun=lambda texture: \
                         dict(tex_sampler=texture), data=texture)
        self.add_uniform("point_size", vartype="float", ndim=1, data=texsize)
        
        # Vertex shader
        self.add_vertex_main("""
    gl_PointSize = point_size;
        """)
        