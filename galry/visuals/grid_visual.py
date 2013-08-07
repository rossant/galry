from visual import Visual, CompoundVisual
from text_visual import TextVisual
from plot_visual import PlotVisual
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

            
class TicksTextVisual(TextVisual):
    def text_compound(self, text):
        d = super(TicksTextVisual, self).text_compound(text)
        d["text_width"] = 0.#-.2
        return d
    
    def initialize_navigation(self):
        self.add_uniform("scale", vartype="float", ndim=2, data=(1., 1.))
        self.add_uniform("translation", vartype="float", ndim=2, data=(0., 0.))
            
        self.add_vertex_main("""
        
            gl_Position = vec4(position, 0., 1.);
            
            if (axis < .5) {
                gl_Position.x = scale.x * (position.x + translation.x);
            }
            else {
                gl_Position.y = scale.y * (position.y + translation.y);
            }
            
            """,
            position='last', name='navigation')

    def initialize(self, *args, **kwargs):
        super(TicksTextVisual, self).initialize(*args, **kwargs)
        axis = np.zeros(self.size)
        self.add_attribute("axis", ndim=1, vartype="int", data=axis)

        
class TicksLineVisual(PlotVisual):
    def initialize_navigation(self):
        self.add_uniform("scale", vartype="float", ndim=2, data=(1., 1.))
        self.add_uniform("translation", vartype="float", ndim=2, data=(0., 0.))
            
        self.add_vertex_main("""
        
            gl_Position = vec4(position, 0., 1.);
            
            // highlight x.y = 0 axes
            /*if ((abs(gl_Position.x) < .0000000001) || 
                (abs(gl_Position.y) < .0000000001))
                vcolor = vec4(1, 1, 1, .75);
            else*/
            vcolor = vec4(1, 1, 1, .25);
                
            if (axis < .5) {
                gl_Position.x = scale.x * (position.x + translation.x);
            }
            else {
                gl_Position.y = scale.y * (position.y + translation.y);
            }
            
            """,
            position='last', name='navigation')

    def initialize(self, *args, **kwargs):
        # kwargs.update(primitive_type='LINES')
        super(TicksLineVisual, self).initialize(*args, **kwargs)
        self.primitive_type = 'LINES'
        
        axis = np.zeros(self.size)
        self.add_attribute("axis", ndim=1, vartype="int", data=axis)
        
        self.add_varying('vcolor', ndim=4)
        self.add_fragment_main("""
            out_color = vcolor;
        """)
        
        
class GridVisual(CompoundVisual):
    def initialize(self, background_transparent=True, letter_spacing=250.,
        *args, **kwargs):
        # add lines visual
        self.add_visual(TicksLineVisual, name='lines',
            position=np.zeros((1,2)),
            **kwargs)
            
        # add the text visual
        self.add_visual(TicksTextVisual, text='',
            fontsize=14, color=(1., 1., 1., .75), name='text',
            letter_spacing=letter_spacing,
            background_transparent=background_transparent,
            **kwargs)
        
        
