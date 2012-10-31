import numpy as np
from default_template import DefaultTemplate
from datatemplate import OLDGLSL
from ..primitives import PrimitiveType
    
class ParallelSignalsTemplate(DefaultTemplate):
    def initialize(self, nplots=None, nsamples=None, **kwargs):
        
        assert nplots is not None
        assert nsamples is not None
        assert self.size == nplots * nsamples
        
        bounds = np.arange(0, self.size + 1, nsamples)
        plot_index = np.repeat(np.arange(nplots), nsamples)
        
        
        self.set_rendering_options(primitive_type=PrimitiveType.LineStrip,
            bounds=bounds)
        
        self.add_attribute("position", vartype="float", ndim=2)

        self.add_attribute("plot_index", vartype="int", ndim=1,
            data=plot_index)
            
        self.add_uniform("colors", vartype="float", ndim=3, size=nplots)
        self.add_varying("plot_color", vartype="float", ndim=3)
        
        self.add_vertex_main("""
    plot_color = colors[int(plot_index)];
        """)
        
        self.add_fragment_main("""
    out_color = vec4(plot_color, 1.0);
        """)
        
        # add navigation code
        # super(ParallelSignalsTemplate, self).initialize(**kwargs)
        self.initialize_default(**kwargs)
        
        
