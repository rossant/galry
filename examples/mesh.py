from galry import *
import OpenGL.GL as gl
import numpy as np
# import numpy.random as rnd
# from galry import InteractionEvents as events
# from galry import UserActions as actions
Qt = QtCore.Qt

"""
The code in this example is adapted from an example in Glumpy:
http://code.google.com/p/glumpy/
"""

def load_obj(filename):
    '''
    Load vertices and faces from a wavefront .obj file and generate normals.
    '''
    data = np.genfromtxt(filename, dtype=[('type', np.character, 1),
                                          ('points', np.float32, 3)])

    # Get vertices and faces
    vertices = data['points'][data['type'] == 'v']
    faces = (data['points'][data['type'] == 'f']-1).astype(np.uint32)

    # Build normals
    T = vertices[faces]
    N = np.cross(T[::,1 ]-T[::,0], T[::,2]-T[::,0])
    L = np.sqrt(N[:,0]**2+N[:,1]**2+N[:,2]**2)
    N /= L[:, np.newaxis]
    normals = np.zeros(vertices.shape)
    normals[faces[:,0]] += N
    normals[faces[:,1]] += N
    normals[faces[:,2]] += N
    L = np.sqrt(normals[:,0]**2+normals[:,1]**2+normals[:,2]**2)
    normals /= L[:, np.newaxis]

    # Scale vertices such that object is contained in [-1:+1,-1:+1,-1:+1]
    vmin, vmax =  vertices.min(), vertices.max()
    vertices = 2*(vertices-vmin)/(vmax-vmin) - 1

    return vertices, normals, faces

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
    
class MyPaintManager(PaintManager):
    """Display a 3D cube that can be rotated, translated, and scaled."""
    
    def transform_view(self):
        """Upload the transformation matrices as a function of the
        interaction variables in the InteractionManager."""
        translation = self.interaction_manager.get_translation()
        rotation = self.interaction_manager.get_rotation()
        scale = self.interaction_manager.get_scaling()
        for visual in self.get_visuals():
            if not visual.get('is_static', False):
                self.set_data(visual=visual['name'], 
                              transform=get_transform(translation, rotation, scale[0]))

    def initialize(self):
        # Important: tells Galry to activate depth buffer
        self.set_rendering_options(activate3D=True)
        
        vertices, normals, faces = load_obj("images/mesh.obj")
        n = len(vertices)
        
        # face colors
        color = (vertices + 1) / 2.
        color = np.hstack((color, np.ones((n, 1))))
        
        # render it as a set of triangles
        self.add_visual(ThreeDimensionsVisual,
                            primitive_type='TRIANGLES',
                            position=vertices, color=color, normal=normals,
                            index=faces.ravel())
                       
        
class MyInteractionManager(InteractionManager):
    """InteractionManager adapted for 3D."""
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
        
        
class MyBindings(DefaultBindingSet):
    def set_panning_mouse(self):
        # Panning: CTRL + left button mouse
        self.set('LeftButtonMouseMoveAction', 'PanEvent',
                    key_modifier='Control',
                    param_getter=lambda p: (-2*p["mouse_position_diff"][0],
                                            -2*p["mouse_position_diff"][1]))
        
    def set_rotation_mouse(self):
        # Rotation: left button mouse
        self.set('LeftButtonMouseMoveAction', 'RotationEvent',
                    param_getter=lambda p: (3*p["mouse_position_diff"][0],
                                            3*p["mouse_position_diff"][1]))    
             
    def set_rotation_keyboard(self):
        """Set zooming bindings with the keyboard."""
        # Rotation: ALT + key arrows
        self.set('KeyPressAction', 'RotationEvent',
                    key='Left', key_modifier='Shift', 
                    param_getter=lambda p: (-.25, 0))
        self.set('KeyPressAction', 'RotationEvent',
                    key='Right', key_modifier='Shift', 
                    param_getter=lambda p: (.25, 0))
        self.set('KeyPressAction', 'RotationEvent',
                    key='Up', key_modifier='Shift', 
                    param_getter=lambda p: (0, .25))
        self.set('KeyPressAction', 'RotationEvent',
                    key='Down', key_modifier='Shift', 
                    param_getter=lambda p: (0, -.25))
                    
    def set_zoombox_mouse(self):
        """Deactivate zoombox."""
        pass

    def set_zoombox_keyboard(self):
        """Deactivate zoombox."""
        pass
    
    def extend(self):
        """Set rotation interactions with mouse and keyboard."""
        self.set_rotation_mouse()
        self.set_rotation_keyboard()
        
        
if __name__ == '__main__':                            
    window = show_basic_window(paint_manager=MyPaintManager,
                               interaction_manager=MyInteractionManager,
                               bindings=MyBindings,
                               antialiasing=True,  # better for 3D rendering
                               constrain_navigation=False,
                               constrain_ratio=True,
                               )

