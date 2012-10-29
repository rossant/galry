import numpy as np
import os
from default_template import DefaultTemplate
from ..primitives import PrimitiveType
from fontmaps import load_font
import matplotlib.pyplot as plt
from ..debugtools import log_debug, log_info, log_warn

class TextTemplate(DefaultTemplate):
    def position_compound(self, position=None):
        if position is None:
            position = (0., 0.)
        position = np.tile(np.array(position).reshape((1, -1)), self.size)
        return dict(position=position)
    
    def text_compound(self, text):
        text_map = self.get_map(text)
        offset = np.hstack((0., np.cumsum(text_map[:, 2])[:-1]))    
        return dict(text_map=self.get_map(text), offset=offset)
    
    def initialize_font(self, font, fontsize):
        self.texture, self.matrix, self.get_map = load_font(font, fontsize)
        
    def initialize(self, font="segoe", fontsize=24, **kwargs):
        self.set_rendering_options(primitive_type=PrimitiveType.Points)

        # text = kwargs.get("text", "")
        # if not text:
            # log_warn("please specify the text to display")
        
        text_length = self.size
        self.set_size(text_length)
        
        # font = kwargs.get("font", "segoe")
        # fontsize = kwargs.get("fontsize", 24)
        self.initialize_font(font, fontsize)
        
        index = np.arange(text_length)
        point_size = float(self.matrix[:,4].max() * self.texture.shape[1])
        # print point_size, self.matrix#[:,-1].max()
        # add navigation code
        super(TextTemplate, self).initialize(**kwargs)
        
        # template attributes and varyings
        self.add_attribute("position", vartype="float", ndim=2,
            default=np.zeros((text_length, 2)))
        self.add_attribute("index", vartype="int", ndim=1, default=index)
        self.add_attribute("offset", vartype="float", ndim=1)#, default=offset)
        self.add_attribute("text_map", vartype="float", ndim=4)#, default=map)
        self.add_varying("flat_text_map", vartype="float", flat=True, ndim=4)
        
        # texture
        self.add_texture("tex_sampler", size=self.texture.shape[:2], ndim=2,
                            ncomponents=self.texture.shape[2],
                            default=self.texture)
        
        # compound variables
        self.add_compound("text", fun=self.text_compound)
        self.add_compound("pos", fun=self.position_compound)
        
        # pure heuristic
        letter_spacing = 100 + 18. * fontsize
        self.add_uniform("letter_spacing", vartype="float", ndim=1,
                            default=letter_spacing)
        self.add_uniform("point_size", vartype="float", ndim=1,
                            default=point_size)
        self.add_uniform("color", vartype="float", ndim=4,
            default=self.default_color)
        
        self.add_vertex_main("""
    gl_Position.x += offset * letter_spacing / window_size.x;
    gl_PointSize = point_size;
    flat_text_map = text_map;
        """)
        
        self.add_fragment_main("""
    float x = gl_PointCoord.x;
    float y = gl_PointCoord.y;
    float w = flat_text_map.z;
    float h = flat_text_map.w;
    
    float delta = h / w;
    x = delta * x;
    if ((x >= 0) && (x <= 1))
    {
        float xcoord = w * x;
        float ycoord = h * y;
        vec2 coord = flat_text_map.xy + vec2(xcoord, ycoord);
        vec4 texcol = texture(tex_sampler, coord);
        out_color = texcol * color;
    }
    else
        out_color = vec4(0, 0, 0, 0);

    // DEBUG
    //out_color = vec4(0, 0, 1, 1);
    //out_color.xw = 1.;  
        """)
       