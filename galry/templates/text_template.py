import numpy as np
import os
from default_template import DefaultTemplate
from ..primitives import PrimitiveType
from fontmaps import load_font
import matplotlib.pyplot as plt
from ..debugtools import log_debug, log_info, log_warn

class TextTemplate(DefaultTemplate):
    def initialize(self, text="", fontsize=24, position=None, color=None,
                **kwargs):
        
        text_length = len(text)
        self.set_size(text_length)
        
        if position is None:
            position = (0., 0.)
        position = np.tile(np.array(position).reshape((1, -1)), text_length)
        
        if color is None:
            color = self.default_color
        
        texture, get_map = load_font(font="segoe", size=fontsize)
        
        map = get_map(text)
        index = np.arange(text_length)
        
        point_size = float(map[0,3] * texture.shape[1])
        
        # add navigation code
        super(TextTemplate, self).initialize(**kwargs)
        
        self.set_rendering_options(primitive_type=PrimitiveType.Points)

        self.add_compounds("text", fun=lambda text: dict(
                                        text_map=get_map(text)))
        self.add_attribute("position", vartype="float", ndim=2, default=position)
        self.add_attribute("index", vartype="int", ndim=1, default=index)
        self.add_attribute("text_map", vartype="float", ndim=4, default=map)
        self.add_varying("flat_text_map", vartype="float", flat=True, ndim=4)
        
        # pure heuristic
        letter_spacing = 100 + 18. * fontsize
        self.add_uniform("letter_spacing", vartype="float", ndim=1,
                            default=letter_spacing)
        
        offset = np.hstack((0., np.cumsum(map[:, 2])[:-1]))
        # offset = np.cumsum(map[:, 2] + .01)
        self.add_attribute("offset", vartype="float", ndim=1, default=offset)
        
        self.add_texture("tex_sampler", size=texture.shape[:2], ndim=2,
                            ncomponents=texture.shape[2],
                            default=texture)
        self.add_uniform("point_size", vartype="float", ndim=1,
                            default=point_size)
        # self.add_uniform("text_length", vartype="int", ndim=1,
                            # default=text_length)
        self.add_uniform("color", vartype="float", ndim=4,
                            default=color)
        
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

        """)
       