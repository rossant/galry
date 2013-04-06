"""GPU-based HSV color space example."""

FSH = """
vec3 Hue(float H)
{
    float R = abs(H * 6 - 3) - 1;
    float G = 2 - abs(H * 6 - 2);
    float B = 2 - abs(H * 6 - 4);
    return vec3(clamp(R, 0, 1), clamp(G, 0, 1), clamp(B, 0, 1));
}

vec4 HSVtoRGB(vec3 HSV)
{
    return vec4(((Hue(HSV.x) - 1) * HSV.y + 1) * HSV.z,1);
}

vec4 RGBtoHSV(vec3 RGB)
{
    vec3 HSV = vec3(0., 0., 0.);
    HSV.z = max(RGB.r, max(RGB.g, RGB.b));
    float M = min(RGB.r, min(RGB.g, RGB.b));
    float C = HSV.z - M;
    if (C != 0)
    {
        HSV.y = C / HSV.z;
        vec3 Delta = (HSV.z - RGB) / C;
        Delta.rgb -= Delta.brg;
        Delta.rg += vec2(2,4);
        if (RGB.r >= HSV.z)
            HSV.x = Delta.b;
        else if (RGB.g >= HSV.z)
            HSV.x = Delta.r;
        else
            HSV.x = Delta.g;
        HSV.x = fract(HSV.x / 6);
    }
    return vec4(HSV,1);
}
"""

VS = """
//gl_PointSize = 600;
//tr = vec4(translation, scale);
//position = (position/scale-translation);

"""

FS = """
vec2 v = varying_tex_coords;
/*vec2 t = vec2(tr.x,-tr.y);
v = (v-t)/tr.zw;*/

out_color = HSVtoRGB(vec3(v.x,v.y,u));
"""

import numpy as np
from galry import *

class MV(TextureVisual):
    def initialize(self, *args, **kwargs):
        super(MV, self).initialize(*args, **kwargs)
        self.add_uniform('u', ndim=1, data=u)
        # pos = np.zeros((1, 2))
        # self.size = 1
        # self.primitive_type = 'POINTS'
        # self.add_attribute('position', ndim=2, vartype='float', data=pos)
        # self.add_varying('tr', ndim=4)
        
    def initialize_fragment(self):
        self.add_fragment_header(FSH)
        # self.add_vertex_main(VS)
        self.add_fragment_main(FS)
        
u = 1.
def change_color(fig, param):
    global u
    du = param
    u += du
    fig.set_data(u=u)

figure(constrain_navigation=True)
visual(MV)
action('KeyPress', change_color, key='Up', key_modifier='Shift', param_getter=.01)
action('KeyPress', change_color, key='Down', key_modifier='Shift', param_getter=-.01)
show()


