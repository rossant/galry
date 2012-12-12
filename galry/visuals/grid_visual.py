from visual import Visual, CompoundVisual
from text_visual import TextVisual
import numpy as np


# Axes
# ----
class AxesVisual(Visual):
    """Axes visual."""
    def initialize_navigation(self):
        self.add_uniform("scale", vartype="float", ndim=2, data=(1., 1.))
        self.add_uniform("translation", vartype="float", ndim=2, data=(0., 0.))
                             
        self.add_vertex_main("""
            vec2 position_tr = position;
            if (axis == 0)
                position_tr.y = scale.y * (position.y + translation.y);
            else if (axis == 1)
                position_tr.x = scale.x * (position.x + translation.x);
            gl_Position = vec4(position_tr, 0., 1.);
            """, position='last', name='navigation')
            
    def initialize(self):
        position = np.array([[-1, 0],
                             [1, 0.],
                             [0, -1],
                             [0., 1]])
                             
        self.size = position.shape[0]
        self.primitive_type = 'LINES'
        self.default_color = (1., 1., 1., .5)
        
        axis = np.zeros(self.size, dtype=np.int32)
        axis[2:] = 1
        
        self.add_attribute("position", ndim=2, data=position)
        self.add_attribute("axis", ndim=1, vartype='int', data=axis)


# Shaders
VSH = """
float nicenum(float x, bool round) {
    float e = floor(log(x) / log(10.));
    float f = x / pow(10., e);
    float nf = 0;
    if (round) {
        if (f < 1.5)
            nf = 1.;
        else if (f < 3)
            nf = 2.;
        else if (f < 7.)
            nf = 5.;
        else
            nf = 10.;
    }
    else {
        if (f <= 1)
            nf = 1.;
        else if (f <= 2)
            nf = 2.;
        else if (f <= 5.)
            nf = 5.;
        else
            nf = 10.;
    }
    return nf * pow(10, e);
}

vec2 get_ticks(vec2 x) {
    int nticks = 10;
    float r = nicenum(x.y - x.x, false);
    float d = nicenum(r / (nticks - 1), true);
    float g0 = floor(x.x / d) * d;
    //float g1 = ceil(x.y / d) * d;
    //float nfrac = max(-floor(log10(d)), 0);
    return vec2(g0, d);
}

"""

VH = """
    vec2 position_tr = position;
    vec2 ticks = vec2(0, 0);
    float tick = 0.;

    // axis position
    if (mod(axis, 2) == 0) {
        %TICKSX%
        ticks = get_ticks(vec2(-translation.x - 1./scale.x, -translation.x + 1./scale.x));
        tick = ticks.x + ticks.y * (1 + index);
        position_tr.x = scale.x * (tick + translation.x);
    }
    else if (mod(axis, 2) == 1) {
        %TICKSY%
        ticks = get_ticks(vec2(-translation.y - 1./scale.y, -translation.y + 1./scale.y));
        tick = ticks.x + ticks.y * (1 + index);
        position_tr.y = scale.y * (tick + translation.y);
    }

    //position_tr = position_tr + vec2(.5, .5);
    
    vtick = tick;
    gl_Position = vec4(position_tr, 0., 1.);
"""

TICKSX = {
    True: """       
        if (axis == 0)
            position_tr.y = -1;
        else
            position_tr.y = 1;
    """,
    False: """
        position_tr.y = scale.y * (position.y + translation.y);
    """
}

TICKSY = {
    True: """       
        if (axis == 1)
            position_tr.x = -1;
        else
            position_tr.x = 1;
    """,
    False: """
        position_tr.x = scale.x * (position.x + translation.x);
    """
}


class TicksGridVisual(Visual):
    def initialize_navigation(self):
        self.add_uniform("scale", vartype="float", ndim=2, data=(1., 1.))
        self.add_uniform("translation", vartype="float", ndim=2, data=(0., 0.))
        
        self.add_vertex_header(VSH)
        
        vh = VH
        vh = vh.replace('%TICKSX%', TICKSX[self.showgrid])
        vh = vh.replace('%TICKSY%', TICKSY[self.showgrid])
        
        self.add_vertex_main(vh, position='last', name='navigation')
            
    def initialize(self, showgrid=False):
        # prevent constraining ratio
        # self.constrain_ratio = False
        
        self.showgrid = showgrid
        n = 10
        
        if not showgrid:
            self.primitive_type = 'POINTS'
            position = np.zeros((2 * n, 2))
            
            # axis 
            axis = np.repeat(np.arange(2), n)
            
            # index of the tick
            index = np.tile(np.arange(n), 2)
            
        else:
            self.primitive_type = 'LINES'
            position = np.zeros((4 * n, 2))
        
            # axis 
            axis = np.tile(2 * np.arange(2), n)
            axis = np.hstack((axis, axis + 1))
            
            # index of the tick
            index = np.tile(np.repeat(np.arange(n), 2), 2)
            
        self.size = position.shape[0]
        
        self.add_attribute("position", ndim=2, data=position)
        self.add_attribute("axis", ndim=1, vartype='int', data=axis)
        self.add_attribute("index", ndim=1, vartype='int', data=index)
        self.add_varying("vaxis", ndim=1, vartype='int')
        self.add_varying("vtick", ndim=1, vartype='float')
            
        self.add_vertex_main("""
            vaxis = axis;
            gl_PointSize = 11;
        """)
        
        if not showgrid:
            self.add_fragment_main("""
            
                // define the tick texture
                out_color = vec4(1, 1, 1, 0);
                float a = .5 / 11;
                
                // alpha channel
                float alpha = .5;
                    
                if (mod(vaxis, 2) == 0) {
                    if ((gl_PointCoord.x > .5 - a) && (gl_PointCoord.x < .5 + a))
                        out_color.w = alpha;
                }
                else if (mod(vaxis, 2) == 1) {
                    if ((gl_PointCoord.y > .5 - a) && (gl_PointCoord.y < .5 + a))
                        out_color.w = alpha;
                }
            """)
        else:
            self.add_fragment_main("""
            
                // alpha channel
                float alpha = .25;
                
                if (abs(vtick) < .0000000000001)
                    alpha = .75;
                    
                // define the tick texture
                out_color = vec4(1, 1, 1, alpha);
            """)

            
class TicksTextVisual(TextVisual):
    def text_compound(self, text):
        d = super(TicksTextVisual, self).text_compound(text)
        d["text_width"] = 0.#-.2
        
        # d['index'] = np.zeros(self.size)
        return d
    
    def initialize_navigation(self):
        self.add_uniform("scale", vartype="float", ndim=2, data=(1., 1.))
        self.add_uniform("translation", vartype="float", ndim=2, data=(0., 0.))
            
        # self.add_vertex_main("""
        
            # gl_Position = vec4(position, 0., 1.);
            
            # if (axis < .5) {
                # gl_Position.x = scale.x * (position.x + translation.x);
            # }
            # else {
                # gl_Position.y = scale.y * (position.y + translation.y);
            # }
            
            # """,
            # position='last', name='navigation')
            
            

        self.add_vertex_header(VSH)
        
        vh = VH
        vh = vh.replace('%TICKSX%', TICKSX[True])
        vh = vh.replace('%TICKSY%', TICKSY[True])
        
        self.add_vertex_main(vh, position='last', name='navigation')
            
    def initialize(self, *args, **kwargs):
        super(TicksTextVisual, self).initialize(*args, **kwargs)
        axis = np.zeros(self.size)
        axis[self.size/2:] = 1
        self.add_attribute("axis", ndim=1, vartype="int", data=axis)
        
        # index of the tick
        index = np.zeros(self.size)
        # index = np.tile(np.arange(self.size), 2)
        
        # self.add_attribute("index", ndim=1, vartype='int', data=index)
        self.add_varying("vaxis", ndim=1, vartype='int')
        self.add_varying("vtick", ndim=1, vartype='float')

        
class GridVisual(CompoundVisual):
    def initialize(self, *args, **kwargs):
        # add lines visual
        self.add_visual(TicksGridVisual, showgrid=True, name='lines', **kwargs)
        # add the text visual
        self.add_visual(TicksTextVisual, text='',
            fontsize=14, color=(1., 1., 1., .75), name='text',
            letter_spacing=250., #prevent_constrain=True,
            **kwargs)
        
        
