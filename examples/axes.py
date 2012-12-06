from galry import *
import numpy as np


# # http://books.google.co.uk/books?id=fvA7zLEFWZgC&lpg=PA61&hl=fr&pg=PA62#v=onepage&q&f=false
# def nicenum(x, round=False):
    # e = np.floor(np.log10(x))
    # f = x / 10 ** e
    # if round:
        # if f < 1.5:
            # nf = 1.
        # elif f < 3:
            # nf = 2.
        # elif f < 7.:
            # nf = 5.
        # else:
            # nf = 10.
    # else:
        # if f <= 1:
            # nf = 1.
        # elif f <= 2:
            # nf = 2.
        # elif f <= 5.:
            # nf = 5.
        # else:
            # nf = 10.
    # return nf * 10 ** e
    
# def get_ticks(x0, x1):
    # nticks = 5
    # r = nicenum(x1 - x0, False)
    # d = nicenum(r / (nticks - 1), True)
    # g0 = np.floor(x0 / d) * d
    # g1 = np.ceil(x1 / d) * d
    # # nfrac = max(-np.floor(np.log10(d)), 0)
    # return np.arange(g0, g1 + .5 * d, d)
  




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

  

VSH = """

float nicenum(float x, bool round) {
    float e = floor(log10(x));
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




class TicksVisual(Visual):
    def initialize_navigation(self):
        self.add_uniform("scale", vartype="float", ndim=2, data=(1., 1.))
        self.add_uniform("translation", vartype="float", ndim=2, data=(0., 0.))
        
        self.add_vertex_header(VSH)
        
        if not self.showgrid:
            self.add_vertex_main("""
            
                vec2 position_tr = position;
                
                vec2 ticksx = get_ticks(vec2(-translation.x - 1./scale.x, -translation.x + 1./scale.x));
                vec2 ticksy = get_ticks(vec2(-translation.y - 1./scale.y, -translation.y + 1./scale.y));
                
                // axis position
                if (mod(axis, 2) == 0) {
                    position_tr.y = scale.y * (position.y + translation.y);
                    position_tr.x = scale.x * (ticksx.x + ticksx.y * (1 + index) + translation.x);
                }
                else if (mod(axis, 2) == 1) {
                    position_tr.x = scale.x * (position.x + translation.x);
                    position_tr.y = scale.y * (ticksy.x + ticksy.y * (1 + index) + translation.y);
                }
                
                gl_Position = vec4(position_tr, 0., 1.);
                """, position='last', name='navigation')
        else:
            self.add_vertex_main("""
            
                vec2 position_tr = position;
                
                vec2 ticksx = get_ticks(vec2(-translation.x - 1./scale.x, -translation.x + 1./scale.x));
                vec2 ticksy = get_ticks(vec2(-translation.y - 1./scale.y, -translation.y + 1./scale.y));
                
                // axis position
                if (mod(axis, 2) == 0) {
                    if (axis == 0)
                        position_tr.y = -1;
                    else
                        position_tr.y = 1;
                    position_tr.x = scale.x * (ticksx.x + ticksx.y * (1 + index) + translation.x);
                }
                else if (mod(axis, 2) == 1) {
                    if (axis == 1)
                        position_tr.x = -1;
                    else
                        position_tr.x = 1;
                    position_tr.y = scale.y * (ticksy.x + ticksy.y * (1 + index) + translation.y);
                }
                
                gl_Position = vec4(position_tr, 0., 1.);
                """, position='last', name='navigation')
            
            
    def initialize(self, showgrid=False):
        self.showgrid = showgrid
        n = 10
        
        if not showgrid:
            position = np.zeros((2 * n, 2))
            
            # axis 
            axis = np.repeat(np.arange(2), n)
            
            # index of the tick
            index = np.tile(np.arange(n), 2)
            
            self.primitive_type = 'POINTS'
        else:
            position = np.zeros((4 * n, 2))
        
            # axis 
            axis = np.tile(2 * np.arange(2), n)
            axis = np.hstack((axis, axis + 1))
            
            # index of the tick
            index = np.tile(np.repeat(np.arange(n), 2), 2)
            # index = np.tile(np.arange(n), 4)
            
            # self.primitive_type = 'POINTS'
            self.primitive_type = 'LINES'
        
        self.size = position.shape[0]
        
        
        self.add_attribute("position", ndim=2, data=position)
        self.add_attribute("axis", ndim=1, vartype='int', data=axis)
        self.add_attribute("index", ndim=1, vartype='int', data=index)
        self.add_varying("vaxis", ndim=1, vartype='int')
            
        self.add_vertex_main("""
            vaxis = axis;
            gl_PointSize = 11;
        """)
        
        if not showgrid:
            self.add_fragment_main("""
                // define the tick texture
                out_color = vec4(1, 1, 1, 0);
                float a = .5 / 11;
                if (mod(vaxis, 2) == 0) {
                    if ((gl_PointCoord.x > .5 - a) && (gl_PointCoord.x < .5 + a))
                        out_color.w = .5;
                }
                else if (mod(vaxis, 2) == 1) {
                    if ((gl_PointCoord.y > .5 - a) && (gl_PointCoord.y < .5 + a))
                        out_color.w = .5;
                }
            """)
        else:
            self.add_fragment_main("""
                // define the tick texture
                out_color = vec4(1, 1, 1, .25);
            """)


class MyPaintManager(PaintManager):
    def initialize(self):
        # axes
        self.add_visual(AxesVisual)
        # ticks
        self.add_visual(TicksVisual, showgrid=True)
        
        self.add_visual(PlotVisual, position=np.random.randn(1000, 2) * .2,
            primitive_type='POINTS')
        

show_basic_window(paint_manager=MyPaintManager)
