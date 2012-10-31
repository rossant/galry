import numpy as np
from default_template import DefaultTemplate
# from datatemplate import OLDGLSL
from ..primitives import PrimitiveType
    
class TextureTemplate(DefaultTemplate):
    def initialize(self, shape=None, ndim=2, ncomponents=4, points=None,
                    # texture=None,
                    **kwargs):

        self.set_size(4)
        self.set_rendering_options(primitive_type=PrimitiveType.TriangleStrip)
        
        if points is None:
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
        tex_coords[0,:] = (0, 1)
        tex_coords[1,:] = (1, 1)
        tex_coords[2,:] = (0, 0)
        tex_coords[3,:] = (1, 0)
        
        self.add_attribute("position", vartype="float", ndim=2,
            data=position)
        
        self.add_attribute("tex_coords", vartype="float", ndim=2,
            data=tex_coords)
        
        if "texture" in kwargs:
            texture= kwargs["texture"]
            shape = texture.shape[:2]
            ncomponents = texture.shape[2]
        
        self.add_texture("tex_sampler", size=shape, ndim=ndim,
            ncomponents=ncomponents)
        # HACK: to avoid conflict in GLSL shader with the "texture" function
        # we redirect the "texture" variable here to "tex_sampler" which
        # is the real name of the variable in the shader
        self.add_compound("texture", fun=lambda data: dict(tex_sampler=data))
        
        self.add_varying("varying_tex_coords", vartype="float", ndim=2)
        
        self.add_vertex_main("""
    varying_tex_coords = tex_coords;
        """)
        
        fragment = """
    out_color = texture(tex_sampler, varying_tex_coords);
        """
        
        # OLDGLSL does not know the texture function
        # if OLDGLSL:
            # fragment = fragment.replace("texture(", "texture%dD(" % 2)
            
        self.add_fragment_main(fragment)
            
        # add navigation code
        # super(TextureTemplate, self).initialize(**kwargs)
        self.initialize_default(**kwargs)
        
        
