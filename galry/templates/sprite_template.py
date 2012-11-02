import numpy as np
from default_template import DefaultTemplate
# from datatemplate import OLDGLSL
from ..primitives import PrimitiveType
    
class SpriteTemplate(DefaultTemplate):
    def get_initialize_arguments(self, **data):
        texture = data.get("texture", None)
        assert texture is not None
        texsize = max(texture.shape[:2])
        
        ncomponents = texture.shape[2]
        
        position = data.get("position", None)
        assert position is not None
        self.size = position.shape[0]
        
        return dict(texsize=texsize, ncomponents=ncomponents)
        
    
    def initialize(self, texsize=None, ncomponents=4, **kwargs):
        
        shape = (texsize, texsize)
        
        self.primitive_type = PrimitiveType.Points

        self.add_attribute("position", vartype="float", ndim=2)
        self.add_attribute("color", vartype="float", ndim=4)
        
        self.add_texture("tex_sampler", size=shape, ndim=2,
            ncomponents=ncomponents)
            
        self.add_compound("texture", fun=lambda texture: dict(tex_sampler=texture))
            
        self.add_uniform("point_size", vartype="float", ndim=1, data=texsize)
        self.add_varying("varying_color", vartype="float", ndim=4)
        
        self.add_vertex_main("""
    gl_PointSize = point_size;
    varying_color = color;
        """)
        
        fragment = """
    out_color = texture(tex_sampler, gl_PointCoord) * varying_color;
        """
        
        # OLDGLSL does not know the texture function
        # if OLDGLSL:
            # fragment = fragment.replace("texture(", "texture%dD(" % 2)
        
        self.add_fragment_main(fragment)
        
        # add navigation code
        # super(SpriteTemplate, self).initialize(**kwargs)
        self.initialize_default(**kwargs)
        
        
