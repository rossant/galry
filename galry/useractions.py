from python_qt_binding.QtCore import Qt 
from tools import enum

__all__ = [
'UserActions',
'UserActionGenerator',
]

# List of user actions.
UserActions = enum(
    "MouseMoveAction",
    "LeftButtonClickAction",
    "MiddleButtonClickAction",
    "RightButtonClickAction",
    "LeftButtonMouseMoveAction",
    "MiddleButtonMouseMoveAction",
    "RightButtonMouseMoveAction",
    "DoubleClickAction",
    "WheelAction",
    "KeyPressAction",
)

def get_maximum_norm(p1, p2):
    """Return the inf norm between two points."""
    return max(abs(p1[0]-p2[0]), abs(p1[1]-p2[1]))
    
class UserActionGenerator(object):
    """Raise user action events.
    
    Define what is the current user action, from the QT events related to mouse 
    and keyboard.
    
    """
    def get_pos(self, pos):
        """Return the coordinate of a position object."""
        return (pos.x(), pos.y())
        
    def __init__(self):
        """Reinitialize the actions."""
        self.action = None
        self.key = None
        self.key_modifier = None
        # mouse button: 0 = no mouse button, 1 = left, 2 = right
        self.mouse_button = 0
        self.mouse_position = (0, 0)
        self.mouse_position_diff = (0, 0)##
        self.mouse_press_position = (0, 0)##
        self.wheel = 0
        
    def get_action_parameters(self):
        """Return an action parameter object."""
        return dict(mouse_position=self.mouse_position,
                    mouse_position_diff=self.mouse_position_diff,
                    mouse_press_position=self.mouse_press_position,
                    wheel=self.wheel,
                    key_modifier=self.key_modifier,
                    key=self.key)
                    
    def clean_action(self):
        """Reset the current action."""
        self.action = None
        
    def mousePressEvent(self, e):
        self.mouse_button = e.button()
        self.mouse_press_position = self.mouse_position = self.get_pos(e.pos())
        
    def mouseDoubleClickEvent(self, e):
        self.action = UserActions.DoubleClickAction
        
    def mouseReleaseEvent(self, e):
        if get_maximum_norm(self.mouse_position,
                    self.mouse_press_position) < 10:
            if self.mouse_button == Qt.LeftButton:
                self.action = UserActions.LeftButtonClickAction
            elif self.mouse_button == Qt.MiddleButton:
                self.action = UserActions.MiddleButtonClickAction
            elif self.mouse_button == Qt.RightButton:
                self.action = UserActions.RightButtonClickAction
        # otherwise, terminate the current action
        else:
            self.action = None
        self.mouse_button = 0
        
    def mouseMoveEvent(self, e):
        pos = self.get_pos(e.pos())
        self.mouse_position_diff = (pos[0] - self.mouse_position[0],
                                    pos[1] - self.mouse_position[1])
        self.mouse_position = pos
        if self.mouse_button == Qt.LeftButton:
            self.action = UserActions.LeftButtonMouseMoveAction
        elif self.mouse_button == Qt.MiddleButton:
            self.action = UserActions.MiddleButtonMouseMoveAction
        elif self.mouse_button == Qt.RightButton:
            self.action = UserActions.RightButtonMouseMoveAction
        else:
            self.action = UserActions.MouseMoveAction
            
    def keyPressEvent(self, e):
        key = e.key()
        # set key_modifier only if it is Ctrl, Shift, Alt or AltGr    
        if key in (Qt.Key_Control, Qt.Key_Shift, Qt.Key_Alt, Qt.Key_AltGr):
            self.key_modifier = key
        else:
            self.action = UserActions.KeyPressAction
            self.key = key
            
    def keyReleaseEvent(self, e):
        if e.key() in (Qt.Key_Control, Qt.Key_Shift, Qt.Key_Alt, Qt.Key_AltGr):
            self.key_modifier = None
        else:
            self.key = None
            
    def wheelEvent(self, e):
        self.wheel = e.delta()
        self.action = UserActions.WheelAction
    