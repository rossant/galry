import numpy as np
from default_template import DefaultTemplate
from plot_template import PlotTemplate
from ..primitives import PrimitiveType
    
class RectanglesTemplate(PlotTemplate):
    def coordinates_compound(self, data):
        if type(data) is tuple:
            data = np.array(data, dtype=np.float32).reshape((1, -1))
        # reorder coordinates to make sure that first corner is lower left
        # corner
        data[:,0], data[:,2] = data[:,[0, 2]].min(axis=1), data[:,[0, 2]].max(axis=1)
        data[:,1], data[:,3] = data[:,[1, 3]].min(axis=1), data[:,[1, 3]].max(axis=1)
        
        nprimitives = data.shape[0]
        x0, y0, x1, y1 = data.T
        
        # create vertex positions, 4 per rectangle
        position = np.zeros((4 * nprimitives,2), dtype=np.float32)
        position[0::4,0] = x0
        position[0::4,1] = y0
        position[1::4,0] = x1
        position[1::4,1] = y0
        position[2::4,0] = x0
        position[2::4,1] = y1
        position[3::4,0] = x1
        position[3::4,1] = y1
        
        return dict(position=position)
    
    def colors_compound(self, data):
        if type(data) is tuple:
            data = np.array(data, dtype=np.float32).reshape((1, -1))
        data = np.repeat(data, 4, axis=0)
        return dict(color=data)
    
    def initialize(self, nprimitives=1, **kwargs):
        self.set_size(4 * nprimitives)
        bounds = np.arange(0, self.size + 1, 4)
        self.set_rendering_options(primitive_type=PrimitiveType.TriangleStrip,
            bounds=bounds)
        
        super(RectanglesTemplate, self).initialize(single_color=False,
            nprimitives=nprimitives, **kwargs)
            
        self.add_compound("coordinates", fun=self.coordinates_compound)
        self.add_compound("colors", fun=self.colors_compound)
        
        
