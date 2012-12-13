from navigation_processor import NavigationEventProcessor
from galry import scale_matrix, rotation_matrix, translation_matrix
import numpy as np

def get_transform(translation, rotation, scale):
    """Return the transformation matrix corresponding to a given
    translation, rotation, and scale.
    
    Arguments:
      * translation: the 3D translation vector,
      * rotation: the 2D rotation coefficients
      * scale: a float with the scaling coefficient.
    
    Returns:
      * M: the 4x4 transformation matrix.
      
    """
    # translation is a vec3, rotation a vec2, scale a float
    S = scale_matrix(scale, scale, scale)
    R = rotation_matrix(rotation[0], axis=1)
    R = np.dot(R, rotation_matrix(rotation[1], axis=0))
    T = translation_matrix(*translation)
    return np.dot(S, np.dot(R, T))
    

class MeshNavigationEventProcessor(NavigationEventProcessor):
    def pan(self, parameter):
        """3D pan (only x,y)."""
        self.tx += parameter[0]
        self.ty += parameter[1]
        
    def zoom(self, parameter):
        """Zoom."""
        dx, px, dy, py = parameter
        if (dx >= 0) and (dy >= 0):
            dx, dy = (max(dx, dy),) * 2
        elif (dx <= 0) and (dy <= 0):
            dx, dy = (min(dx, dy),) * 2
        else:
            dx = dy = 0
        self.sx *= np.exp(dx)
        self.sy *= np.exp(dy)
        self.sxl = self.sx
        self.syl = self.sy
        
    def get_translation(self):
        return self.tx, self.ty, self.tz
        
    def transform_view(self):
        """Upload the transformation matrices as a function of the
        interaction variables in the InteractionManager."""
        translation = self.get_translation()
        rotation = self.get_rotation()
        scale = self.get_scaling()
        for visual in self.paint_manager.get_visuals():
            if not visual.get('is_static', False):
                self.set_data(visual=visual['name'], 
                              transform=get_transform(translation, rotation, scale[0]))
                              
                         