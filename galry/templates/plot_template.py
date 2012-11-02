import numpy as np
from default_template import DefaultTemplate
from ..primitives import PrimitiveType
    
class PlotTemplate(DefaultTemplate):
    def get_initialize_arguments(self, **data):
        position = data.get("position", None)
        assert position is not None
        # nprimitives, nsamples = position.shape
        
        self.size = position.shape[0]
        
        color = data.get("color", self.default_color)
        
        # handle the case where there is a single color given as a list of
        # RGB components instead of a tuple
        if type(color) is list:
            assert color
            if color and (type(color[0]) != tuple) and (3 <= len(color) <= 4):
                color = tuple(color)
            else:
                color = np.array(color)
        
        use_color_array = False
        if isinstance(color, np.ndarray):
            colors_ndim = color.shape[1]
            # first case: one color per point
            if color.shape[0] == self.size:
                single_color = False
            # second case: use a color array so that each plot has a single
            # color, this saves memory since there is a single color in
            # memory for any plot
            else:
                use_color_array = True
                single_color = False
        elif type(color) is tuple:
            single_color = True
            colors_ndim = len(color)
        
        assert single_color is not None
        assert colors_ndim
        
        return dict(single_color=single_color, colors_ndim=colors_ndim,
            use_color_array=use_color_array,
            # nprimitives=nprimitives, nsamples=nsamples
            )
    
    def initialize(self, colors_ndim=4, single_color=True, 
        nprimitives=1, nsamples=None,use_color_array=False, **kwargs):
        
        assert self.size
        
        if nprimitives == 1:
            nsamples = self.size
        if nsamples is None:
            nsamples = self.size // nprimitives
        
        assert nprimitives
        assert nsamples
        
        # set position attribute
        self.add_attribute("position", vartype="float", ndim=2, 
                           data=np.zeros((self.size, 2)))
            
        bounds = np.arange(0, self.size + 1, nsamples)
        # self.set_rendering_options(bounds=bounds)
        self.bounds = bounds
        
        # single color case: no need for a color buffer, just use default color
        if single_color:
            self.add_uniform("color", vartype="float", ndim=colors_ndim,
                data=self.default_color)
            
            if colors_ndim == 3:
                self.add_fragment_main("""
            out_color = vec4(color, 1.0);
                """)
            elif colors_ndim == 4:
                self.add_fragment_main("""
            out_color = color;
                """)
            
        # multiple colors case: color attribute
        elif not use_color_array:
            self.add_attribute("color", vartype="float", ndim=colors_ndim,
                data=np.tile(self.default_color[:colors_ndim], (self.size, 1)))
            self.add_varying("varying_color", vartype="float", ndim=colors_ndim)
            
            self.add_vertex_main("""
        varying_color = color;
            """)
            
            if colors_ndim == 3:
                self.add_fragment_main("""
            out_color = vec4(varying_color, 1.0);
                """)
            elif colors_ndim == 4:
                self.add_fragment_main("""
            out_color = varying_color;
                """)
                
        # multiple colors, but with a color array to save memory
        elif use_color_array:
            plot_index = np.repeat(np.arange(nprimitives), nsamples)
            
            self.add_attribute("plot_index", vartype="int", ndim=1,
                data=plot_index)
                
            self.add_uniform("color", vartype="float", ndim=colors_ndim, size=nprimitives)
            self.add_varying("varying_color", vartype="float", ndim=colors_ndim)
            
            self.add_vertex_main("""
        varying_color = color[int(plot_index)];
            """)
            
            if colors_ndim == 3:
                self.add_fragment_main("""
            out_color = vec4(varying_color, 1.0);
                """)
            elif colors_ndim == 4:
                self.add_fragment_main("""
            out_color = varying_color;
                """)

        # add navigation code
        # super(PlotTemplate, self).initialize(**kwargs)
        self.initialize_default(**kwargs)
        