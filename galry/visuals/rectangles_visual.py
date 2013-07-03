import numpy as np
from plot_visual import PlotVisual
from galry import get_color
    
class RectanglesVisual(PlotVisual):
    """Template for displaying one or several rectangles. This template
    derives from PlotTemplate."""
    
    def coordinates_compound(self, data):
        """Compound function for the coordinates variable.
        
        Arguments:
          * data: a Nx4 array where each line contains the coordinates of the
            rectangle corners as (x0, y0, x1, y1)
        
        Returns:
          * dict(position=position): the coordinates of all vertices used
            to render the rectangles as TriangleStrips.
        
        """
        if type(data) is tuple:
            data = np.array(data, dtype=np.float32).reshape((1, -1))
        # reorder coordinates to make sure that first corner is lower left
        # corner
        data[:,0], data[:,2] = data[:,[0, 2]].min(axis=1), data[:,[0, 2]].max(axis=1)
        data[:,1], data[:,3] = data[:,[1, 3]].min(axis=1), data[:,[1, 3]].max(axis=1)
        
        nprimitives = data.shape[0]
        x0, y0, x1, y1 = data.T
        
        # create vertex positions, 4 per rectangle
        position = np.zeros((4 * nprimitives, 2), dtype=np.float32)
        position[0::4,0] = x0
        position[0::4,1] = y0
        position[1::4,0] = x1
        position[1::4,1] = y0
        position[2::4,0] = x0
        position[2::4,1] = y1
        position[3::4,0] = x1
        position[3::4,1] = y1
        
        return dict(position=position)
    
    def initialize(self, coordinates=None, color=None, autocolor=None,
        depth=None, autonormalizable=True):
        
        if type(coordinates) is tuple:
            coordinates = np.array(coordinates, dtype=np.float32).reshape((1, -1))
        nprimitives = coordinates.shape[0]
        
        if autocolor is not None:
            color = get_color(autocolor)
        
        if color is None:
            color = self.default_color
            
        # If there is one color per rectangle, repeat the color array so
        # that there is one color per vertex.
        if isinstance(color, np.ndarray):
            if color.shape[0] == nprimitives:
                color = np.repeat(color, 4, axis=0)
        
        # there are four vertices per rectangle
        self.size = 4 * nprimitives
        self.primitive_type = 'TRIANGLE_STRIP'
        self.bounds = np.arange(0, self.size + 1, 4)
        

        position = self.coordinates_compound(coordinates)['position']
        
        super(RectanglesVisual, self).initialize(position=position, 
            color=color, nprimitives=nprimitives,
            autonormalizable=autonormalizable)# depth=depth)
            
        self.add_compound("coordinates", fun=self.coordinates_compound, 
            data=coordinates)
            
        self.depth = depth