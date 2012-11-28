import numpy as np
from visual import Visual
    
class SpriteVisual(Visual):
    """Template displaying one texture in multiple positions with
    different colors."""
    
    def initialize(self, texture=None, position=None, color=None):
        texsize = float(max(texture.shape[:2]))
        shape = texture.shape
        ncomponents = texture.shape[2]
        self.size = position.shape[0]
        # texsize = shape[:2]
        
        if shape[0] == 1:
            self.ndim = 1
        elif shape[0] > 1:
            self.ndim = 2
        
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
            
            
        texture_shader = """
        out_color = texture%NDIM%(tex_sampler, gl_PointCoord%POINTCOORD%) * %COLOR%;
        """
            
        
        shader_ndim = "%dD" % self.ndim
        if self.ndim == 1:
            shader_pointcoord = ".x"
        else:
            shader_pointcoord = ""
            
        # single color case: no need for a color buffer, just use default color
        if single_color:
            self.add_uniform("color", ndim=colors_ndim, data=color)   
            shader_color_name = "color"
        # multiple colors case: color attribute
        else:
            self.add_attribute("color", ndim=colors_ndim, data=color)
            self.add_varying("varying_color", vartype="float", ndim=colors_ndim)
            self.add_vertex_main("""
            varying_color = color;
            """)
            shader_color_name = "varying_color"
            
        if colors_ndim == 3:
            shader_color = "vec4(%s, 1.0)" % shader_color_name
        elif colors_ndim == 4:
            shader_color = shader_color_name
        
        texture_shader = texture_shader.replace('%COLOR%', shader_color)
        texture_shader = texture_shader.replace('%NDIM%', shader_ndim)
        texture_shader = texture_shader.replace('%POINTCOORD%', shader_pointcoord)
        self.add_fragment_main(texture_shader)
        
        # add variables
        self.add_attribute("position", vartype="float", ndim=2, data=position)
        self.add_texture("tex_sampler", size=shape, ndim=self.ndim,
            ncomponents=ncomponents)
        self.add_compound("texture", fun=lambda texture: \
                         dict(tex_sampler=texture), data=texture)
        self.add_uniform("point_size", vartype="float", ndim=1, data=texsize)
        
        # Vertex shader
        self.add_vertex_main("""
    gl_PointSize = point_size;
        """)
        