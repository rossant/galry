import numpy as np
import os
from galry import log_debug, log_info, log_warn, get_color
from fontmaps import load_font
from visual import Visual

__all__ = ['TextVisual']

VS = """
gl_Position.x += (offset - text_width / 2) * spacing.x / window_size.x;
gl_Position.y -= index * spacing.y / window_size.y;

gl_Position.xy = gl_Position.xy + posoffset / window_size;

gl_PointSize = point_size;
flat_text_map = text_map;
"""

def FS(background_transparent=True):
    if background_transparent:
        background_transparent_shader = "letter_alpha"
    else:
        background_transparent_shader = "1."
    fs = """
// relative coordinates of the pixel within the sprite (in [0,1])
float x = gl_PointCoord.x;
float y = gl_PointCoord.y;

// size of the corresponding character
float w = flat_text_map.z;
float h = flat_text_map.w;

// display the character at the left of the sprite
float delta = h / w;
x = delta * x;
if ((x >= 0) && (x <= 1))
{
    // coordinates of the character in the font atlas
    vec2 coord = flat_text_map.xy + vec2(w * x, h * y);
    float letter_alpha = texture2D(tex_sampler, coord).a;
    out_color = color * letter_alpha;
    out_color.a = %s;
}
else
    out_color = vec4(0, 0, 0, 0);
""" % background_transparent_shader
    return fs


class TextVisual(Visual):
    """Template for displaying short text on a single line.
    
    It uses the following technique: each character is rendered as a sprite,
    i.e. a pixel with a large point size, and a single texture for every point.
    The texture contains a font atlas, i.e. all characters in a given font.
    Every point comes with coordinates that indicate which small portion
    of the font atlas to display (that portion corresponds to the character).
    This is all done automatically, thanks to a font atlas stored in the
    `fontmaps` folder. There needs to be one font atlas per font and per font
    size. Also, there is a configuration text file with the coordinates and
    size of every character. The software used to generate font maps is
    AngelCode Bitmap Font Generator.
    
    For now, there is only the Segoe font.
    
    """
                
    def position_compound(self, coordinates=None):
        """Compound variable with the position of the text. All characters
        are at the exact same position, and are then shifted in the vertex
        shader."""
        if coordinates is None:
            coordinates = (0., 0.)
        if type(coordinates) == tuple:
            coordinates = [coordinates]
            
        coordinates = np.array(coordinates)
        position = np.repeat(coordinates, self.textsizes, axis=0)
        return dict(position=position)
    
    def text_compound(self, text):
        """Compound variable for the text string. It changes the text map,
        the character position, and the text width."""
        
        coordinates = self.coordinates
        
        if "\n" in text:
            text = text.split("\n")
            
        if type(text) == list:
            self.textsizes = [len(t) for t in text]
            text = "".join(text)
            if type(coordinates) != list:
                coordinates = [coordinates] * len(self.textsizes)
            index = np.repeat(np.arange(len(self.textsizes)), self.textsizes)
            text_map = self.get_map(text)
            
            # offset for all characters in the merging of all texts
            offset = np.hstack((0., np.cumsum(text_map[:, 2])[:-1]))
            
            # for each text, the cumsum of the length of all texts strictly
            # before
            d = np.hstack(([0], np.cumsum(self.textsizes)[:-1]))
            
            # compensate the offsets for the length of each text
            offset -= np.repeat(offset[d], self.textsizes)
            
            text_width = 0.
                
        else:
            self.textsizes = len(text)
            text_map = self.get_map(text)
            offset = np.hstack((0., np.cumsum(text_map[:, 2])[:-1]))    
            text_width = offset[-1]
            index = np.zeros(len(text))
            
        self.size = len(text)
        
        d = dict(text_map=text_map, offset=offset, text_width=text_width,
            index=index)
        d.update(self.position_compound(coordinates))
        
        return d
    
    def initialize_font(self, font, fontsize):
        """Initialize the specified font at a given size."""
        self.texture, self.matrix, self.get_map = load_font(font, fontsize)

    def initialize(self, text, coordinates=(0., 0.), font='segoe', fontsize=24,
            color=None, letter_spacing=None, interline=0., autocolor=None,
            background_transparent=True,
            prevent_constrain=False, depth=None, posoffset=None):
        """Initialize the text template."""
        
        if prevent_constrain:
            self.constrain_ratio = False
            
        if autocolor is not None:
            color = get_color(autocolor)
            
        if color is None:
            color = self.default_color
        
        self.size = len(text)
        self.primitive_type = 'POINTS'
        self.interline = interline
        
        text_length = self.size
        self.initialize_font(font, fontsize)
        self.coordinates = coordinates
        
        point_size = float(self.matrix[:,4].max() * self.texture.shape[1])

        # template attributes and varyings
        self.add_attribute("position", vartype="float", ndim=2, data=np.zeros((self.size, 2)))
            
        self.add_attribute("offset", vartype="float", ndim=1)
        self.add_attribute("index", vartype="float", ndim=1)
        self.add_attribute("text_map", vartype="float", ndim=4)
        self.add_varying("flat_text_map", vartype="float", flat=True, ndim=4)
       
        if posoffset is None:
            posoffset = (0., 0.)
        self.add_uniform('posoffset', vartype='float', ndim=2, data=posoffset)
       
        # texture
        self.add_texture("tex_sampler", size=self.texture.shape[:2], ndim=2,
                            ncomponents=self.texture.shape[2],
                            data=self.texture)
        
        # pure heuristic (probably bogus)
        if letter_spacing is None:
            letter_spacing = (100 + 17. * fontsize)
        self.add_uniform("spacing", vartype="float", ndim=2,
                            data=(letter_spacing, interline))
        self.add_uniform("point_size", vartype="float", ndim=1,
                            data=point_size)
        # one color per
        if isinstance(color, np.ndarray) and color.ndim > 1:
            self.add_attribute('color0', vartype="float", ndim=4, data=color)
            self.add_varying('color', vartype="float", ndim=4)
            self.add_vertex_main('color = color0;')
        else:
            self.add_uniform("color", vartype="float", ndim=4, data=color)
        self.add_uniform("text_width", vartype="float", ndim=1)
        
        # compound variables
        self.add_compound("text", fun=self.text_compound, data=text)
        self.add_compound("coordinates", fun=self.position_compound, data=coordinates)

        # vertex shader
        self.add_vertex_main(VS, after='viewport')

        # fragment shader
        self.add_fragment_main(FS(background_transparent))
        
        self.depth = depth