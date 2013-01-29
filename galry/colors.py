import re
import numpy as np

__all__ = ['get_color', 'get_next_color']

HEX = '0123456789abcdef'
HEX2 = dict((a+b, (HEX.index(a)*16 + HEX.index(b)) / 255.) \
             for a in HEX for b in HEX)

def rgb(triplet):
    triplet = triplet.lower()
    if triplet[0] == '#':
        triplet = triplet[1:]
    if len(triplet) == 6:
        return (HEX2[triplet[0:2]], HEX2[triplet[2:4]], HEX2[triplet[4:6]],
                1.)
    elif len(triplet) == 8:
        return (HEX2[triplet[0:2]], HEX2[triplet[2:4]], HEX2[triplet[4:6]],
                HEX2[triplet[6:8]])

def triplet(rgb):
    return format((rgb[0]<<16)|(rgb[1]<<8)|rgb[2], '06x')

BASIC_COLORS_STRING = "rgbcymkw"
BASIC_COLORS = [
    (1., 0., 0.),
    (0., 1., 0.),
    (0., 0., 1.),
    (0., 1., 1.),
    (1., 1., 0.),
    (1., 0., 1.),
    (0., 0., 0.),
    (1., 1., 1.),
]
COLORMAP = [4, 1, 0, 3, 2, 5]

def get_next_color(i):
    return BASIC_COLORS[COLORMAP[np.mod(i, 6)]]

def get_basic_color(color):
    col = BASIC_COLORS[BASIC_COLORS_STRING.index(color)]
    return col + (1.,)
    
def get_basic_color_alpha(color):
    r = re.match("([a-z])([0-9\.]*)", color)
    if r is not None:
        col, alpha = r.groups()
        col = BASIC_COLORS[BASIC_COLORS_STRING.index(col)]
        return col + (float(alpha),)

def get_hexa_color(color):
    return rgb(color)
    
PATTERNS = {
    '^[a-z]{1}$': get_basic_color,
    '^[a-z]{1}[0-9\.]*$': get_basic_color_alpha,
    '^[#a-z0-9]{6,9}$': get_hexa_color,
}
  
def get_color(color):
    """Return a color RGBA normalized coefficients from any of the following
    possible inputs:
      * (r, g, b) or (r, g, b, a) with r, g, b, a between 0 and 1.
      * a string with one of the following characters: rgbcymkw for the
        primary colors, and optionnaly a floating number between 0 and 1 for 
        the alpha channel, ie 'r.75' for red at 75%.
      * a string with an hexadecimal code.
      * a list of colors
    
    """
    if type(color) == int:
        color = get_next_color(color)
    if isinstance(color, basestring):
        color = color.lower()
        for pattern, fun in PATTERNS.iteritems():
            r = re.match(pattern, color)
            if r is not None:
                break
        return fun(color)
    elif type(color) is tuple:
        assert color
        if len(color) == 3:
            color = color + (1.,)
        assert len(color) == 4
        return color
    elif type(color) is list:
        assert color
        if color and (type(color[0]) != tuple) and (3 <= len(color) <= 4):
            color = tuple(color)
        return map(get_color, color)
    else:
        return color

if __name__ == '__main__':
    
    print get_color(['r','y.5'])
    
   

