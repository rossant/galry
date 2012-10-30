import numpy as np
from default_template import DefaultTemplate
from ..primitives import PrimitiveType
    
class PlotTemplate(DefaultTemplate):
    def initialize(self, colors_ndim=4, single_color=True, 
        nprimitives=1, nsamples=None, **kwargs):
        
        assert self.size
        
        if nprimitives == 1:
            nsamples = self.size
        if nsamples is None:
            nsamples = self.size // nprimitives
        
        assert nprimitives
        assert nsamples
        
        # infer size from positions if positions are given
        # if positions is not None:
            # self.set_size(positions.shape[0])
            
        # set position attribute
        self.add_attribute("position", vartype="float", ndim=2,
            # default=np.zeros((self.size, 2))
            )
            
        # bounds = np.arange(0, self.size + 1, nsamples)
        # self.set_rendering_options(bounds=bounds)
            
        # infer number of color components
        # if colors is None:
            # colors_ndim = len(self.default_color)
            # colors = self.default_color
        # elif isinstance(colors, np.ndarray):
            # colors_ndim = colors.shape[1]
            
        # single color case: no need for a color buffer, just use default color
        if single_color:
            # colors_ndim = len(colors)
            # self.set_default_color(colors)
            self.add_uniform("color", vartype="float", ndim=colors_ndim,
                default=self.default_color)
            
            if colors_ndim == 3:
                self.add_fragment_main("""
            out_color = vec4(color, 1.0);
                """)
            elif colors_ndim == 4:
                self.add_fragment_main("""
            out_color = color;
                """)
            
        # multiple colors case: color attribute
        else:
            self.add_attribute("color", vartype="float", ndim=colors_ndim,
                default=np.zeros((self.size, colors_ndim)))
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
                
        
        
        # add navigation code
        super(PlotTemplate, self).initialize(**kwargs)
        