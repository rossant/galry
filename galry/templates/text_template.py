import numpy as np
import os
from default_template import DefaultTemplate
from ..primitives import PrimitiveType
import matplotlib.pyplot as plt
from ..debugtools import log_debug, log_info, log_warn

def load_texture(size, font=None):
    if font is None:
        font = "monospace"
    possible_sizes = np.array([18, 20, 22, 24, 28, 32])
    ind = np.nonzero(size - possible_sizes <= 0)[0]
    if len(ind) == 0:
        i = len(possible_sizes) - 1
    else:
        i = ind[0]
    char_width = possible_sizes[i]
    filename = "%s%d" % (font, char_width)
    log_info("loading %s" % filename)
    # get the absolute path of the file
    path = os.path.dirname(os.path.realpath(__file__))
    # load the texture from an image
    font_atlas = plt.imread(os.path.join(path, "../fonts/%s.png" % filename))
    return font_atlas, char_width

CHARACTERS = """abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ12134567890.:,;'"(!?)+-*/= """
n = int(np.ceil(np.sqrt(len(CHARACTERS))))

def get_character_index(text, c):
    try:
        return CHARACTERS.index(c)
    except:
        return len(CHARACTERS) - 1

def get_character_coordinates(text):
    ind = [get_character_index(text, c) for c in text]
    icoords = np.array([(np.mod(i, n), i / n) for i in ind])
    return icoords
    
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
        
        point_size = float(fontsize)
        
        font_atlas, char_width = load_texture(fontsize)
        total_width = float(font_atlas.shape[1])

        icoords = get_character_coordinates(text)
        index = np.arange(text_length)

        # add navigation code
        super(TextTemplate, self).initialize(**kwargs)
        
        self.set_rendering_options(primitive_type=PrimitiveType.Points)

        self.add_compounds("text", fun=lambda text:
                            dict(icoords=get_character_coordinates(text)))
        
        self.add_attribute("position", vartype="float", ndim=2, default=position)
        
        self.add_attribute("index", vartype="int", ndim=1, default=index)
        
        self.add_attribute("icoords", vartype="int", ndim=2, default=icoords)
        
        self.add_varying("varying_icoords", vartype="int", flat=True, ndim=2)
        
        self.add_texture("tex_sampler", size=font_atlas.shape[:2], ndim=2,
                            ncomponents=font_atlas.shape[2],
                            default=font_atlas)
        
        self.add_uniform("point_size", vartype="float", ndim=1,
                            default=point_size)
        
        self.add_uniform("char_width", vartype="float", ndim=1,
                            default=char_width)

        self.add_uniform("total_width", vartype="float", ndim=1,
                            default=total_width)
        
        self.add_uniform("text_length", vartype="int", ndim=1,
                            default=text_length)

        self.add_uniform("color", vartype="float", ndim=4,
                            default=color)
        
        self.add_vertex_main("""
    float text_width = text_length * point_size * .9 / window_size.x;
    gl_Position.x += (text_width / text_length) * (index - (text_length - 1) / 2.);
    gl_PointSize = point_size;
    varying_icoords = icoords;
        """)
        
        self.add_fragment_main("""
    vec2 coord = char_width / total_width * (varying_icoords + gl_PointCoord);
    out_color = texture(tex_sampler, coord) * color;
        """)
       