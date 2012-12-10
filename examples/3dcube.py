from galry import *
import OpenGL.GL as gl
import numpy as np
import numpy.random as rnd
# from galry import InteractionEvents as events
# from galry import UserActions as actions
Qt = QtCore.Qt

def create_cube(color, scale=1.):
    """Create a cube as a set of independent triangles.
    
    Arguments:
      * color: the colors of each face, as a 6*4 array.
      * scale: the scale of the cube, the ridge length is 2*scale.
    
    Returns:
      * position: a Nx3 array with the positions of the vertices.
      * normal: a Nx3 array with the normals for each vertex.
      * color: a Nx3 array with the color for each vertex.
    
    """
    position = np.array([
        # Front
        [-1., -1., -1.],
        [1., -1., -1.],
        [-1., 1., -1.],
        
        [1., 1., -1.],
        [-1., 1., -1.],
        [1., -1., -1.],
        
        # Right
        [1., -1., -1.],
        [1., -1., 1.],
        [1., 1., -1.],
        
        [1., 1., 1.],
        [1., 1., -1.],
        [1., -1., 1.],
        
        # Back
        [1., -1., 1.],
        [-1., -1., 1.],
        [1., 1., 1.],
        
        [-1., 1., 1.],
        [1., 1., 1.],
        [-1., -1., 1.],
        
        # Left
        [-1., -1., 1.],
        [-1., -1., -1.],
        [-1., 1., 1.],
        
        [-1., 1., -1.],
        [-1., 1., 1.],
        [-1., -1., -1.],
        
        # Bottom
        [1., -1., 1.],
        [1., -1., -1.],
        [-1., -1., 1.],
        
        [-1., -1., -1.],
        [-1., -1., 1.],
        [1., -1., -1.],
        
        # Top
        [-1., 1., -1.],
        [-1., 1., 1.],
        [1., 1., -1.],
        
        [1., 1., 1.],
        [1., 1., -1.],
        [-1., 1., 1.],
    ])
    
    normal = np.array([
        # Front
        [0., 0., -1.],
        [0., 0., -1.],
        [0., 0., -1.],

        [0., 0., -1.],
        [0., 0., -1.],
        [0., 0., -1.],
        
        # Right
        [1., 0., 0.],
        [1., 0., 0.],
        [1., 0., 0.],

        [1., 0., 0.],
        [1., 0., 0.],
        [1., 0., 0.],
        
        # Back
        [0., 0., 1.],
        [0., 0., 1.],
        [0., 0., 1.],

        [0., 0., 1.],
        [0., 0., 1.],
        [0., 0., 1.],
        
        # Left
        [-1., 0., 0.],
        [-1., 0., 0.],
        [-1., 0., 0.],
        
        [-1., 0., 0.],
        [-1., 0., 0.],
        [-1., 0., 0.],
        
        # Bottom
        [0., -1., 0.],
        [0., -1., 0.],
        [0., -1., 0.],
        
        [0., -1., 0.],
        [0., -1., 0.],
        [0., -1., 0.],
        
        # Top
        [0., 1., 0.],
        [0., 1., 0.],
        [0., 1., 0.],
        
        [0., 1., 0.],
        [0., 1., 0.],
        [0., 1., 0.],
    ])    
    position *= scale
    color = np.repeat(color, 6, axis=0)
    return position, normal, color
    
    
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
        self.set_rendering_options(activate3D = True)
        
        # face colors
        color = np.ones((6, 4))
        color[0,[0,1]] = 0
        color[1,[0,2]] = 0
        color[2,[1,2]] = 0
        color[3,[0]] = 0
        color[4,[1]] = 0
        color[5,[2]] = 0
        
        # create the cube
        position, normal, color = create_cube(color)
        
        # render it as a set of triangles
        self.add_visual(ThreeDimensionsVisual,
                            primitive_type='TRIANGLES',
                            position=position, color=color, normal=normal)
                       
        
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
                               # display_fps=True
                               )
