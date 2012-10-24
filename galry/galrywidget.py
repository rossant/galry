import sys
import time
import numpy as np
import numpy.random as rdn
import OpenGL.GL as gl
import OpenGL.GLUT as glut
from python_qt_binding import QtCore, QtGui
from python_qt_binding.QtCore import Qt, pyqtSignal
from python_qt_binding.QtOpenGL import QGLWidget, QGLFormat
from interactionevents import InteractionEvents as events
from useractions import UserActions as actions
from useractions import UserActionGenerator
import bindingmanager
from debugtools import log_debug, log_info, log_warn
import interactionmanager
import paintmanager
from tools import FpsCounter, show_window

__all__ = [
'GalryWidget',
'AutodestructibleWindow',
'create_custom_widget',
'create_basic_window',
'show_basic_window',
]

# # DEBUG: raise errors if Numpy arrays are unnecessarily copied
# from OpenGL.arrays import numpymodule
# try:
    # numpymodule.NumpyHandler.ERROR_ON_COPY = True
# except Exception as e:
    # print "WARNING: unable to set the Numpy-OpenGL copy warning"

# Set to True or to a number of milliseconds to have all windows automatically
# killed after a fixed time. It is useful for automatic debugging or
# benchmarking.
AUTODESTRUCT = False
DEFAULT_AUTODESTRUCT = 1000

# default manager classes
DEFAULT_MANAGERS = dict(
    paint_manager=paintmanager.PaintManager,
    binding_manager=bindingmanager.BindingManager,
    interaction_manager=interactionmanager.InteractionManager,
)



# Main Galry class.
class GalryWidget(QGLWidget):
    """Efficient interactive 2D visualization widget.
    
    This QT widget is based on OpenGL and depends on both PyQT (or PySide)
    and PyOpenGL. It implements low-level mechanisms for interaction processing
    and acts as a glue between the different managers (PaintManager, 
    BindingManager, InteractionManager).
    """
    # background color as a 4-tuple (R,G,B,A)
    bgcolor = (0,0,0,0)

    # default window size
    width, height = 600, 600
    
    # FPS counter, used for debugging
    fps_counter = FpsCounter()
    display_fps = False

    # widget creation parameters
    events_enum = None
    bindings = None
    companion_classes_initialized = False
    
    # constrain width/height ratio when resizing of zooming
    constrain_ratio = False
    
    # Initialization methods
    # ----------------------
    def __init__(self, format=None, **kwargs):
        super(GalryWidget, self).__init__(format)
        
        # capture key events
        self.setFocusPolicy(Qt.StrongFocus)
        self.setMouseTracking(True)
        
        # Initialize the objects providing the core features of the widget.
        self.user_action_generator = UserActionGenerator()
        
        # initialize objects
        self.events_to_signals = {}
        self.prev_event = None
                                    
        # keyword arguments without "_manager" => passed to initialize                  
        self.initialize(**kwargs)

        # initialize widget parameters
        # initialize companion classes if it has not been done in initialize
        if not self.companion_classes_initialized:
            self.initialize_companion_classes()
        self.initialize_bindings()
        self.initialize_events_enum()
        
    def set_bindings(self, bindings=None):
        """Set the interaction mode by specifying the binding object.
        
        Several binding objects can be given for the binding manager, such that
        the first one is the currently active one.
        
        Arguments:
          * bindings: a list of classes instances deriving from
            ActionEventBindingSet.
            
        """
        if bindings is None:
            bindings = [bindingmanager.DefaultBindingSet()]
        if type(bindings) is not list and type(bindings) is not tuple:
            bindings = [bindings]
        # if binding is a class, try instanciating it
        for i in xrange(len(bindings)):
            if not isinstance(bindings[i], bindingmanager.ActionEventBindingSet):
                bindings[i] = bindings[i]()
        self.bindings = bindings
        
    def set_events_enum(self, events_enum=None):
        """Set the interaction events enumeration."""
        self.events_enum = events_enum
        
    def set_companion_classes(self, **kwargs):
        """Set specified companion classes, unspecified ones are set to
        default classes.
        
        """
        if not hasattr(self, "companion_classes"):
            self.companion_classes = {}
            
        self.companion_classes.update(kwargs)
        # default companion classes
        self.companion_classes.update([(k,v) for k,v in \
            DEFAULT_MANAGERS.iteritems() if k not in self.companion_classes])
        
    def initialize_bindings(self):
        """Initialize the interaction bindings."""
        if self.bindings is None:
            self.set_bindings()
        self.binding_manager.add(*self.bindings)
        # set base cursor: the current binding is the first one
        self.interaction_manager.base_cursor = self.bindings[0].base_cursor
        
    def initialize_events_enum(self):
        """Initialize the extended events enumeration."""
        self.interaction_manager.extend_events(self.events_enum)
        
    def initialize_companion_classes(self):
        """Initialize companion classes."""
        # default companion classes
        if not getattr(self, "companion_classes", None):
            self.set_companion_classes()
        
        # create the managers
        for key, val in self.companion_classes.iteritems():
            obj = val()
            setattr(self, key, obj)
            obj.parent = self
        
        # link all managers
        for key, val in self.companion_classes.iteritems():
            for child_key, child_val in self.companion_classes.iteritems():
                if child_key == key:
                    continue
                obj = getattr(self, key)
                setattr(obj, child_key, getattr(self, child_key))
        self.companion_classes_initialized = True
        
    def initialize(self, **kwargs):
        """
        Parameters such as events_enum, bindings, companion_classes can be
        set here, by overriding this method. If initializations must be done
        after companion classes instanciation, then self.initialize_companion_classes
        can be called here. Otherwise, it will be called automatically after initialize().
        """
        pass
        
    def initialized(self):
        pass
        
    # OpenGL widget methods
    # ---------------------
    def initializeGL(self):
        """Initialize OpenGL parameters."""
        
        # use vertex buffer object
        gl.glEnableClientState(gl.GL_VERTEX_ARRAY)

        # used for multisampling (antialiasing)
        gl.glEnable(gl.GL_MULTISAMPLE)
        gl.glEnable(gl.GL_VERTEX_PROGRAM_POINT_SIZE)
        gl.glEnable(gl.GL_POINT_SPRITE)
        
        # enable transparency
        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
        
        # initialize GLUT
        glut.glutInit()
        
        # initialize data manager and shaders
        self.paint_manager.initialize()
        self.paint_manager.initialize_shaders()
        
        # Paint the background with the specified color (black by default)
        gl.glClearColor(*self.paint_manager.bgcolor)
        
        self.initialized()
        
    def paintGL(self):
        """Paint the scene.
        
        Called as soon as the window needs to be painted (e.g. call to 
        `updateGL()`).
        
        """
        # clear the buffer
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)
        # paint everything
        self.paint_manager.paint_all()
        # paint fps
        if self.display_fps:
            self.paint_fps()
        # flush GL commands
        gl.glFlush()
        # compute FPS
        self.fps_counter.tick()
        
    def paint_fps(self):
        """Display the FPS in the top-right of the screen."""
        fps = "FPS: %d" % int(self.fps_counter.get_fps())
        x, y = self.normalize_position(10, 20)
        self.paint_manager.paint_text(fps, (x, y), (1,1,0))
        
    # Viewport methods
    # ----------------
    def get_viewport(self):
        return self.viewport
        
    def set_viewport(self, viewport):
        self.viewport = viewport
        x0, y0, x1, y1 = viewport
        # set orthographic projection (2D only)
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        gl.glOrtho(x0, x1, y0, y1, -1, 1)
        # all subsequent transformations relate to the model view
        gl.glMatrixMode(gl.GL_MODELVIEW)
        
    def resizeGL(self, width, height):
        """Reinitialize the viewport.
        
        Called when the user resizes the window. 
        
        """
        self.width, self.height = width, height
        
        # paint within the whole window
        gl.glViewport(0, 0, width, height)
        
        # scaled viewport -1/1
        x0 = -1
        x1 = 1
        y0 = -1
        y1 = 1
        # viewport in the case where the ratio should be kept constant
        if self.constrain_ratio:
            a = float(width) / height
            if a > 1:
                x0, x1 = -a, a
            else:
                y0, y1 = -1. / a, 1. / a
        self.set_viewport((x0, y0, x1, y1))
        
    def sizeHint(self):
        return QtCore.QSize(self.width, self.height)
        
    # Event methods
    # -------------
    def mousePressEvent(self, e):
        self.user_action_generator.mousePressEvent(e)
        self.process_interaction()
        
    def mouseReleaseEvent(self, e):
        self.user_action_generator.mouseReleaseEvent(e)
        self.process_interaction()
        
    def mouseDoubleClickEvent(self, e):
        self.user_action_generator.mouseDoubleClickEvent(e)
        self.process_interaction()
        
    def mouseMoveEvent(self, e):
        self.user_action_generator.mouseMoveEvent(e)
        self.process_interaction()
        
    def keyPressEvent(self, e):
        self.user_action_generator.keyPressEvent(e)
        self.process_interaction()
        
    def keyReleaseEvent(self, e):
        self.user_action_generator.keyReleaseEvent(e)
        
    def wheelEvent(self, e):
        self.user_action_generator.wheelEvent(e)
        self.process_interaction()
        
    # Normalization methods
    # ---------------------
    def normalize_position(self, x, y):
        """Window coordinates ==> world coordinates."""
        x0, y0, x1, y1 = self.viewport
        x = x0 + x/float(self.width) * (x1 - x0)
        y = -(y0 + y/float(self.height) * (y1 - y0))
        return x, y
             
    def normalize_diff_position(self, x, y):
        """Normalize the coordinates of a difference vector between two
        points.
        
        """
        x0, y0, x1, y1 = self.viewport
        x = x/float(self.width) * (x1 - x0)
        y = -y/float(self.height) * (y1 - y0)
        return x, y
        
    def normalize_action_parameters(self, parameters):
        """Normalize points in the action parameters object in the window
        coordinate system.
        
        Arguments:
          * parameters: the action parameters object, containing all
            variables related to user actions.
            
        Returns:
           * parameters: the updated parameters object with normalized
             coordinates.
             
        """
        parameters["mouse_position"] = self.normalize_position(\
                                                *parameters["mouse_position"])
        parameters["mouse_position_diff"] = self.normalize_diff_position(\
                                            *parameters["mouse_position_diff"])
        parameters["mouse_press_position"] = self.normalize_position(\
                                            *parameters["mouse_press_position"])
        return parameters
    
    # Signal methods
    # --------------
    def connect_events(self, arg1, arg2):
        """Makes a connection between a QT signal and an interaction event.
        
        The signal parameters must correspond to the event parameters.
        
        Arguments:
          * arg1: a QT bound signal or an interaction event.
          * arg2: an interaction event or a QT bound signal.
        
        """
        if type(arg1) == int:
            self.connect_event_to_signal(arg1, arg2)
        elif type(arg2) == int:
            self.connect_signal_to_event(arg1, arg2)
        else:
            raise TypeError("One of the arguments must be an InteractionEvents \
               enum value")
    
    def connect_signal_to_event(self, signal, event):
        """Connect a QT signal to an interaction event.
        
        The event parameters correspond to the signal parameters.
        
        Arguments:
          * signal: a QT signal.
          * event: an InteractionEvent enum value.
        
        """
        if signal is None:
            raise Exception("The signal %s is not defined" % signal)
        slot = lambda *args, **kwargs: \
                self.process_interaction(event, args, **kwargs)
        signal.connect(slot)
        
    def connect_event_to_signal(self, event, signal):
        """Connect an interaction event to a QT signal.
        
        The event parameters correspond to the signal parameters.
        
        Arguments:
          * event: an InteractionEvent enum value.
          * signal: a QT signal.
        
        """
        self.events_to_signals[event] = signal
        
    # Interaction methods
    # -------------------
    def switch_interaction_mode(self):
        """Switch the interaction mode."""
        binding = self.binding_manager.switch()
        # set base cursor
        self.interaction_manager.base_cursor = binding.base_cursor
        
    def get_current_action(self):
        # get current action
        action = self.user_action_generator.action
        
        # get current key if the action was KeyPressAction
        key = self.user_action_generator.key
        
        # get key modifier
        key_modifier = self.user_action_generator.key_modifier
        
        # retrieve action parameters and normalize with using the
        # window size
        parameters = self.normalize_action_parameters(
                        self.user_action_generator.get_action_parameters())
            
        return action, key, key_modifier, parameters
        
    def get_current_event(self):
        # get the current interaction mode
        binding = self.binding_manager.get()
        
        # get current user action
        action, key, key_modifier, parameters = self.get_current_action()
        
        # get the associated interaction event
        event, param_getter = binding.get(action, key=key,
                                                  key_modifier=key_modifier)
        
        # get the parameter object by calling the param getter
        if param_getter is not None:
            args = param_getter(parameters)
        else:
            args = None
            
        return event, args
        
    def process_interaction(self, event=None, args=None):
        """Process user interaction.
        
        This method is called after each user action (mouse, keyboard...).
        It finds the right action associated to the command, then the event 
        associated to that action.
        """
        if event is None:
            # get current event from current user action
            event, args = self.get_current_event()
        
        # handle interaction mode change
        if event == events.SwitchInteractionModeEvent:
            self.switch_interaction_mode()
        
        # process the interaction event
        self.interaction_manager.process_event(event, args)
        
        # raise a signal if there is one associated to the current event
        if event in self.events_to_signals:
            self.events_to_signals[event].emit(*args)
        
        # set cursor
        self.setCursor(self.interaction_manager.get_cursor())
        
        # clean current action (unique usage)
        self.user_action_generator.clean_action()
        
        # update the OpenGL view
        if event is not None or self.prev_event is not None:
            self.updateGL()
            
        # keep track of the previous event
        self.prev_event = event
    
    def save_image(self, file=None):
        if file is None:
            file = "image.png"
        image = self.grabFrameBuffer()
        image.save(file,"PNG")
    
# Basic widgets helper functions and classes
# ------------------------------------------
def create_custom_widget(bindings=None, events_enum=None, antialiasing=False,
                         constrain_ratio=False,
                        **companion_classes):
    """Helper function to create a custom widget class from various parameters.
    
    Arguments:
      * bindings=None: the bindings class, instance, or a list of those.
      * events_enum=None: an enumeration with the extended interaction events.
      * antialiasing=False: whether to activate antialiasing or not.
    
    """
    class MyWidget(GalryWidget):
        def __init__(self):
            # antialiasing
            format = QGLFormat()
            if antialiasing:
                format.setSampleBuffers(True)
            super(MyWidget, self).__init__(format=format)
        
        def initialize(self):
            self.set_bindings(bindings)
            self.set_events_enum(events_enum)
            self.set_companion_classes(**companion_classes)
            self.constrain_ratio = constrain_ratio

    return MyWidget
    
class AutodestructibleWindow(QtGui.QMainWindow):
    autodestruct = None
    
    def __init__(self, **kwargs):
        super(AutodestructibleWindow, self).__init__()
        # This is important in interaction sessions: it allows the widget
        # to clean everything up as soon as we close the window (otherwise
        # it is just hidden).
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.initialize(**kwargs)
        
    def set_autodestruct(self, autodestruct=None):
        # by default, use global variable
        if autodestruct is None:
            # use the autodestruct option in command line by default
            autodestruct = "autodestruct" in sys.argv
            # print autodestruct
            if autodestruct is False:
                global AUTODESTRUCT
                autodestruct = AUTODESTRUCT
        # option for autodestructing the window after a fixed number of 
        # seconds: useful for automatic testing
        if autodestruct is True:
            # 3 seconds by default, if True
            global DEFAULT_AUTODESTRUCT
            autodestruct = DEFAULT_AUTODESTRUCT
        if autodestruct:
            log_info("window autodestruction in %d second(s)" % (autodestruct / 1000.))
        self.autodestruct = autodestruct
        
    def initialize(self, **kwargs):
        pass
        
    def kill(self):
        if self.autodestruct:
            self.timer.stop()
            self.close()
        
    def showEvent(self, e):
        if self.autodestruct:
            self.timer = QtCore.QTimer()
            self.timer.setInterval(self.autodestruct)
            self.timer.setSingleShot(True)
            self.timer.timeout.connect(self.kill)
            self.timer.start()
            
def create_basic_window(widget=None, size=None, position=(100, 100),
                        autodestruct=None):
    class BasicWindow(AutodestructibleWindow):
        def initialize(self, widget=widget, size=size, position=position,
                       autodestruct=autodestruct):
            """Create a basic window to display a single widget.
            
            Arguments:
              * widget: a widget instance.
              
            """
            self.set_autodestruct(autodestruct)
            # default widget
            if widget is None:
                widget = GalryWidget()
            # if widget is not an instance of GalryWidget, maybe it's a class,
            # then try to instanciate it
            if not isinstance(widget, GalryWidget):
                widget = widget()
            # create widget
            self.widget = widget
            if size is None:
                size = self.widget.width, self.widget.height
            # show widget
            self.setGeometry(*(position + size))
            self.setCentralWidget(self.widget)
            self.show()
            
        def closeEvent(self, e):
            self.widget.paint_manager.cleanup()
            
    return BasicWindow
    
def show_basic_window(widget_class=None, window_class=None, size=None,
            position=(100, 100), autodestruct=None, **kwargs):
    # default widget class
    if widget_class is None:
        widget_class = create_custom_widget(**kwargs)
    # defaut window class
    if window_class is None:
        window_class = create_basic_window(widget_class, size=size,
            position=position, autodestruct=autodestruct)
    # create and show window
    return show_window(window_class)
    