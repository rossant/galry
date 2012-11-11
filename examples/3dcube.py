from galry import *
import OpenGL.GL as gl
import numpy as np
import numpy.random as rnd
from galry import InteractionEvents as events
from galry import UserActions as actions
Qt = QtCore.Qt

def create_cube(color):
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
    position /= 2.
    color = np.repeat(color, 6, axis=0)
    return position, normal, color
    
    
def get_transform(translation, rotation, scale):
    # translation is a vec3, rotation a vec2, scale a float
    S = scale_matrix(scale, scale, scale)
    R = rotation_matrix(rotation[0], axis=1)
    R = np.dot(R, rotation_matrix(rotation[1], axis=0))
    T = translation_matrix(*translation)
    return np.dot(S, np.dot(R, T))
    
    
class MyPaintManager(PaintManager):
    def transform_view(self):
        translation = self.interaction_manager.get_translation()
        rotation = self.interaction_manager.get_rotation()
        scale = self.interaction_manager.get_scaling()
        for dataset in self.datasets:
            if not dataset["template"].is_static:
                self.set_data(dataset=dataset, 
                        transform=get_transform(translation, rotation, scale[0]))

    def initialize(self):
        # tells Galry to activate depth buffer
        self.activate3D = True
        
        color = np.ones((6, 4))
        color[0,[0,1]] = 0
        color[1,[0,2]] = 0
        color[2,[1,2]] = 0
        color[3,[0]] = 0
        color[4,[1]] = 0
        color[5,[2]] = 0
        
        position, normal, color = create_cube(color)

        self.create_dataset(ThreeDimensionsTemplate, primitive_type=PrimitiveType.Triangles,
                            position=position, color=color, normal=normal)
                       
        
class MyInteractionManager(InteractionManager):    
    def pan(self, parameter):
        self.tx += parameter[0]
        self.ty += parameter[1]
        
    def zoom(self, parameter):
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
        # Panning: left button mouse
        self.set(actions.LeftButtonMouseMoveAction, events.PanEvent,
                    key_modifier=Qt.Key_Control,
                    param_getter=lambda p: (-2*p["mouse_position_diff"][0],
                                            -2*p["mouse_position_diff"][1]))
        
    def set_rotation_mouse(self):
        # Panning: left button mouse
        self.set(actions.LeftButtonMouseMoveAction, events.RotationEvent,
                    param_getter=lambda p: (3*p["mouse_position_diff"][0],
                                            3*p["mouse_position_diff"][1]))    
             
                 
    def set_rotation_keyboard(self):
        """Set zooming bindings with the keyboard."""
        # Zooming: ALT + key arrows
        self.set(actions.KeyPressAction, events.RotationEvent,
                    key=Qt.Key_Left, key_modifier=Qt.Key_Shift, 
                    param_getter=lambda p: (-.25, 0))
        self.set(actions.KeyPressAction, events.RotationEvent,
                    key=Qt.Key_Right, key_modifier=Qt.Key_Shift, 
                    param_getter=lambda p: (.25, 0))
        self.set(actions.KeyPressAction, events.RotationEvent,
                    key=Qt.Key_Up, key_modifier=Qt.Key_Shift, 
                    param_getter=lambda p: (0, .25))
        self.set(actions.KeyPressAction, events.RotationEvent,
                    key=Qt.Key_Down, key_modifier=Qt.Key_Shift, 
                    param_getter=lambda p: (0, -.25))
                    
    def set_zoombox_mouse(self):
        pass

    def set_zoombox_keyboard(self):
        pass
    
    def extend(self):
        self.set_rotation_mouse()
        self.set_rotation_keyboard()
        
if __name__ == '__main__':                            
    window = show_basic_window(paint_manager=MyPaintManager,
                               interaction_manager=MyInteractionManager,
                               bindings=MyBindings,
                               antialiasing=True,
                               constrain_navigation=False,
                               display_fps=True)
