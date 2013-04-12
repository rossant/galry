from qtools.qtpy.QtCore import Qt 

__all__ = ['UserActionGenerator', 'LEAP']


def get_maximum_norm(p1, p2):
    """Return the inf norm between two points."""
    return max(abs(p1[0]-p2[0]), abs(p1[1]-p2[1]))
    
# try importing leap motion SDK    
try:
    import Leap
    LEAP = {}
    LEAP['frame'] = None
    class LeapListener(Leap.Listener):
        def on_frame(self, controller):
            try:
                LEAP['frame'] = controller.frame()
            except:
                pass
except:
    # leap SDK not available
    LEAP = {}
    
class UserActionGenerator(object):
    """Raise user action events.
    
    Define what is the current user action, from the QT events related to mouse 
    and keyboard.
    
    """
    def get_pos(self, pos):
        """Return the coordinate of a position object."""
        return (pos.x(), pos.y())
        
    def __init__(self):
        self.reset()
        
    def reset(self):
        """Reinitialize the actions."""
        self.action = None
        self.key = None
        self.key_modifier = None
        self.mouse_button = 0
        self.mouse_position = (0, 0)
        self.mouse_position_diff = (0, 0)
        self.mouse_press_position = (0, 0)
        
        self.pinch_position = (0, 0)
        self.pinch_rotation = 0.
        self.pinch_scale = 1.
        self.pinch_scale_diff = 0.
        self.pinch_start_position = (0, 0)
        
        self.wheel = 0
        self.init_leap()
        
    def init_leap(self):
        if LEAP:
            self.leap_listener = LeapListener()
            self.leap_controller = Leap.Controller()
            self.leap_controller.add_listener(self.leap_listener)
        
    def get_action_parameters(self):
        """Return an action parameter object."""
        mp = self.mouse_position
        mpd = self.mouse_position_diff
        mpp = self.mouse_press_position
        if not mp:
            mp = (0, 0)
        if not mpd:
            mpd = (0, 0)
        if not mpp:
            mpp = (0, 0)
        parameters = dict(mouse_position=mp,
                            mouse_position_diff=mpd,
                            mouse_press_position=mpp,
                            
                            pinch_start_position=self.pinch_start_position,
                            pinch_position=self.pinch_position,
                            pinch_rotation=self.pinch_rotation,
                            pinch_scale=self.pinch_scale,
                            pinch_scale_diff=self.pinch_scale_diff,
                            
                            wheel=self.wheel,
                            key_modifier=self.key_modifier,
                            key=self.key)
        return parameters
                    
    def clean_action(self):
        """Reset the current action."""
        self.action = None

    def pinchEvent(self, e):
        if e.state() == Qt.GestureStarted:
            self.action = 'Pinch'
            self.pinch_start_position = (0, 0)
        elif e.state() == Qt.GestureUpdated:
            self.action = 'Pinch'
            self.pinch_position = self.get_pos(e.centerPoint())
            # Save the pinch start position at the first GestureUpdated event
            if self.pinch_start_position == (0, 0):
                self.pinch_start_position = self.pinch_position
            self.pinch_rotation_diff = e.rotationAngle()
            self.pinch_rotation = e.totalRotationAngle()
            self.pinch_scale_diff = e.scaleFactor() - 1
            self.pinch_scale = e.totalScaleFactor()
        elif e.state() == Qt.GestureFinished:
            self.action = None
            self.pinch_position = (0, 0)
            self.pinch_rotation = 0.
            self.pinch_scale = 1.
            self.pinch_scale_diff = 0.
            self.pinch_start_position = (0, 0)

    def mousePressEvent(self, e):
        self.mouse_button = e.button()
        self.mouse_press_position = self.mouse_position = self.get_pos(e.pos())
        
    def mouseDoubleClickEvent(self, e):
        self.action = 'DoubleClick'
        
    def mouseReleaseEvent(self, e):
        if get_maximum_norm(self.mouse_position,
                    self.mouse_press_position) < 10:
            if self.mouse_button == Qt.LeftButton:
                self.action = 'LeftClick'
            elif self.mouse_button == Qt.MiddleButton:
                self.action = 'MiddleClick'
            elif self.mouse_button == Qt.RightButton:
                self.action = 'RightClick'
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
            self.action = 'LeftClickMove'
        elif self.mouse_button == Qt.MiddleButton:
            self.action = 'MiddleClickMove'
        elif self.mouse_button == Qt.RightButton:
            self.action = 'RightClickMove'
        else:
            self.action = 'Move'
            
    def keyPressEvent(self, e):
        key = e.key()
        # set key_modifier only if it is Ctrl, Shift, Alt or AltGr    
        if key in (Qt.Key_Control, Qt.Key_Shift, Qt.Key_Alt, Qt.Key_AltGr):
            self.key_modifier = key
        else:
            self.action = 'KeyPress'
            self.key = key
            
    def keyReleaseEvent(self, e):
        if e.key() in (Qt.Key_Control, Qt.Key_Shift, Qt.Key_Alt, Qt.Key_AltGr):
            self.key_modifier = None
        else:
            self.key = None
            
    def wheelEvent(self, e):
        self.wheel = e.delta()
        self.action = 'Wheel'
    
    def focusOutEvent(self, e):
        # reset all actions when the focus goes out
        self.reset()
        
    def close(self):
        if LEAP:
            self.leap_controller.remove_listener(self.leap_listener)
        
        