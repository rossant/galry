from galry import QtGui, QtCore, QtOpenGL
from galry import log_info
from QtOpenGL import QGLWidget
import OpenGL.GL as gl


# Low-level OpenGL functions to initialize/load variables
# -------------------------------------------------------
class Attribute(object):
    @staticmethod
    def create():
        """Create a new buffer and return a `buffer` index."""
        return gl.glGenBuffers(1)
        
    @staticmethod
    def bind(buffer, location=None):
        """Bind a buffer and associate a given location."""
        if location >= 0:
            gl.glEnableVertexAttribArray(location)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, buffer)
        
    @staticmethod
    def set_attribute(location, ndim):
        gl.glVertexAttribPointer(location, ndim, gl.GL_FLOAT, gl.GL_FALSE, 0, None)
    
    @staticmethod
    def load(data):
        """Load data in the buffer for the first time. The buffer must
        have been bound before."""
        gl.glBufferData(gl.GL_ARRAY_BUFFER, data, gl.GL_DYNAMIC_DRAW)
        
    @staticmethod
    def update(data, onset=0):
        """Update data in the currently bound buffer."""
        # convert onset into bytes count
        onset *= data.shape[1] * data.itemsize
        gl.glBufferSubData(gl.GL_ARRAY_BUFFER, onset, data)
    
    @staticmethod
    def delete(buffer):
        gl.glDeleteBuffers(1, buffer)
        
        
class Uniform(object):
    @staticmethod
    def create():
        pass
        
    @staticmethod
    def bind():
        pass
    
    @staticmethod
    def load(data):
        pass
        
    @staticmethod
    def update(data):
        pass


class Texture(object):
    @staticmethod
    def create():
        pass
        
    @staticmethod
    def bind():
        pass
    
    @staticmethod
    def load(data):
        pass
        
    @staticmethod
    def update(data):
        pass


# Shader manager
# --------------
class ShaderManager(object):
    def __init__(self, vertex_shader, fragment_shader):
        self.vertex_shader = vertex_shader
        self.fragment_shader = fragment_shader
        # compile shaders
        self.compile()
        # create program
        self.program = self.create_program()

    def compile(self):
        """Compile the shaders."""
        # compile vertex shader
        vs = gl.glCreateShader(gl.GL_VERTEX_SHADER)
        gl.glShaderSource(vs, self.vertex_shader)
        gl.glCompileShader(vs)
        
        result = gl.glGetShaderiv(vs, gl.GL_COMPILE_STATUS)
        # check compilation error
        if not(result):
            msg = "Compilation error:"
            msg += gl.glGetShaderInfoLog(vs)
            msg += self.vertex_shader
            raise RuntimeError(msg)
        
        # compile fragment shader
        fs = gl.glCreateShader(gl.GL_FRAGMENT_SHADER)
        gl.glShaderSource(fs, self.fragment_shader)
        gl.glCompileShader(fs)
        
        result = gl.glGetShaderiv(fs, gl.GL_COMPILE_STATUS)
        # check compilation error
        if not(result):
            msg = "Compilation error:"
            msg += gl.glGetShaderInfoLog(fs)
            msg += self.fragment_shader
            raise RuntimeError(msg)
        
        self.vs, self.fs = vs, fs
        
    def create_program(self):
        """Create shader program and attach shaders."""
        program = gl.glCreateProgram()
        gl.glAttachShader(program, self.vs)
        gl.glAttachShader(program, self.fs)
        gl.glLinkProgram(program)

        result = gl.glGetProgramiv(program, gl.GL_LINK_STATUS)
        # check linking error
        if not(result):
            msg = "Shader program linking error:"
            msg += gl.glGetProgramInfoLog(program)
            raise RuntimeError(msg)
        
        self.program = program
        return program
        
    def get_location(self, name):
        """Return the location of an attribute after the shaders have compiled."""
        return gl.glGetAttribLocation(self.program, name)


# Slicing classes
# ---------------
MAX_VBO_SIZE = 65000

class Slicer(object):
    # def __init__(self, size):
        # self.set_size(size)
    
    def set_size(self, size):
        self.size = size
        
    def slice_count(self):
        # DEBUG
        return 1
    
    def slices(self):
        """Return a list of slices. Each item is a pair (pos, size)
        where pos is the position of that slice in the buffer, and size the
        size of that slice."""
        # DEBUG
        return [(0, self.size)]
       
       
class SlicedAttribute(object):
    def __init__(self, slicer, location):
        self.set_slicer(slicer)
        self.location = location
        # create the sliced buffers
        self.create()
        
    def set_slicer(self, slicer):
        """Set the slicer."""
        self.slicer = slicer
        self.slices = self.slicer.slices()
        self.size = self.slicer.size
        
    def create(self):
        """Create the sliced buffers."""
        self.attributes = [Attribute.create() for _ in self.slices]
    
    def load(self, data):
        """Load data on all sliced buffers."""
        # NOTE: the slicer needs to be updated if the size of the data changes
        for buffer, (pos, size) in zip(self.attributes, self.slices):
            Attribute.bind(buffer, self.location)
            Attribute.load(data[pos:size,:])

    def bind(self, slice):
        Attribute.bind(self.attributes[slice], self.location)
        

# Painter class
# -------------
class Painter(object):
    """Provides low-level methods for calling OpenGL rendering commands."""
    @staticmethod
    def draw_arrays(primtype, offset, size):
        gl.glDrawArrays(gl.GL_POINTS, offset, size)
        
    @staticmethod
    def draw_multi_arrays():
        pass
        
    @staticmethod
    def draw_indexed_arrays():
        pass
        
    @staticmethod
    def draw_indexed_multi_arrays():
        pass


# Visual renderer
# ---------------
class GLVisualRenderer(object):
    """Handle rendering of one visual"""
    
    def __init__(self, visual):
        """Initialize the visual renderer, create the slicer, initialize
        all variables and the shaders."""
        self.visual = visual
        # set the slicer
        self.slicer = Slicer()
        self.update_size(self.visual['size'])
        # compile and link the shaders
        self.shader_manager = ShaderManager(self.visual['vertex_shader'],
                                            self.visual['fragment_shader'])
        # initialize all variables
        self.initialize_variables()
        
    def update_size(self, size):
        """Update the size of the visual, and update the slicer too."""
        self.size = size
        self.slicer.set_size(size)
        self.slices = self.slicer.slices()
    
    
    # Variable methods
    # ----------------
    def get_variables(self, shader_type=None):
        """Return all variables defined in the visual."""
        if not shader_type:
            return self.visual.get('variables', [])
        else:
            return [var for var in self.get_variables() \
                            if var['shader_type'] == shader_type]
        
    def get_variable(self, name):
        """Return a variable by its name."""
        variables = [v for v in self.get_variables() if v.get('name', '') == name]
        if not variables:
            raise ValueError("The variable %s has not been found" % name)
        return variables[0]
        
        
    # Initialization methods
    # ----------------------
    def initialize_variables(self):
        """Initialize all variables, after the shaders have compiled."""
        for var in self.visual['variables']:
            shader_type = var['shader_type']
            # call initialize_***(name) to initialize that variable
            getattr(self, 'initialize_%s' % shader_type)(var['name'])
    
    def initialize_attribute(self, name):
        """Initialize an attribute: get the shader location, create the
        sliced buffers, and load the data."""
        # retrieve the location of that attribute in the shader
        location = self.shader_manager.get_location(name)
        variable = self.get_variable(name)
        variable['location'] = location
        # initialize the sliced buffers
        variable['sliced_attribute'] = SlicedAttribute(self.slicer, location)
        variable['sliced_attribute'].load(variable.get('data', None))
        
    def initialize_texture(self, name):
        pass
        
    def initialize_uniform(self, name):
        pass
        
        
    # Loading methods
    # ---------------
    def load_variables(self):
        pass
        
    def load_attribute(self, name, data):
        pass
        
    def load_texture(self, name, data):
        pass
        
    def load_uniform(self, name, data):
        pass
        
        
    # Updating methods
    # ----------------
    def update_variables(self):
        pass
        
    def update_attribute(self, name, data):
        pass
        
    def update_texture(self, name, data):
        pass
        
    def update_uniform(self, name, data):
        pass
        
        
    # Binding methods
    # ---------------
    def bind_attributes(self, slice):
        """Bind all attributes of the visual for the given slice.
        This method is used during rendering."""
        attributes = self.get_variables('attribute')
        for variable in attributes:
            Attribute.set_attribute(variable['location'], variable['ndim'])
            variable['sliced_attribute'].bind(slice)
            
        
    # Paint methods
    # -------------
    def paint(self):
        for slice in xrange(len(self.slices)):
            self.bind_attributes(slice)
            Painter.draw_arrays(getattr(gl, "GL_%s" % self.visual['primitive_type']), 
                0, 100)

        
# Scene renderer
# --------------
class GLRenderer(object):
    """OpenGL renderer for a Scene.
    
    This class takes a Scene object (dictionary) as an input, and
    renders the scene. It provides methods to update the data in real-time.
    
    """
    # Initialization
    # --------------
    def __init__(self, scene):
        self.scene = scene
    
    def get_renderer_info(self):
        """Return information about the client renderer.
        
        Arguments:
          * info: a dictionary with the following keys:
              * renderer_name
              * opengl_version
              * glsl_version
              
        """
        return {
            'renderer_name': gl.glGetString(gl.GL_RENDERER),
            'opengl_version': gl.glGetString(gl.GL_VERSION),
            'glsl_version': gl.glGetString(gl.GL_SHADING_LANGUAGE_VERSION)
        }
    
    def set_renderer_options(self):
        """Set the OpenGL options."""
        options = self.scene.get('renderer_options', {})
        
        # use vertex buffer object
        gl.glEnableClientState(gl.GL_VERTEX_ARRAY)

        # used for multisampling (antialiasing)
        if options.get('antialiasing', None):
            gl.glEnable(gl.GL_MULTISAMPLE)
            
        # used for sprites
        if options.get('sprites', None):
            gl.glEnable(gl.GL_VERTEX_PROGRAM_POINT_SIZE)
            gl.glEnable(gl.GL_POINT_SPRITE)
        
        # enable transparency
        if options.get('transparency', None):
            gl.glEnable(gl.GL_BLEND)
            gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
            
        # enable depth buffer, necessary for 3D rendering
        if options.get('activate3D', None):
            gl.glEnable(gl.GL_DEPTH_TEST)
            gl.glDepthMask(gl.GL_TRUE)
            gl.glDepthFunc(gl.GL_LEQUAL)
            gl.glDepthRange(0.0, 1.0)
            # TODO: always enable??
            gl.glClearDepth(1.0)
        
        # Paint the background with the specified color (black by default)
        background = options.get('background', (0, 0, 0, 0))
        gl.glClearColor(*background)
        
        
    # Visual methods
    # --------------
    def get_visuals(self):
        """Return all visuals defined in the scene."""
        return self.scene.get('visuals', [])
        
    def get_visual(self, name):
        """Return a visual by its name."""
        visuals = [v for v in self.get_visuals() if v.get('name', '') == name]
        if not visuals:
            raise ValueError("The visual %s has not been found" % name)
        return visuals[0]
        
        
    # Data methods
    # ------------
    def set_data(self, visual, **kwargs):
        """Load data for the specified visual.
        
        Arguments:
          * visual: the name of the visual as a string, or a visual dict.
          * **kwargs: the data to update as name:value pairs. name can be
            any field of the visual, plus one of the following keywords:
              * size: the size of the visual,
              * primitive_type: the GL primitive type,
              * constrain_ratio: whether to constrain the ratio of the visual,
              * constrain_navigation: whether to constrain the navigation,
        
        """
        # retrieve a visual by its name
        if type(visual) == str:
            visual = self.get_visual(visual)
        
        
    # Rendering methods
    # -----------------
    def initialize(self):
        """Initialize the renderer."""
        # print the renderer information
        for key, value in self.get_renderer_info().iteritems():
            log_info(key + ": " + value)
        # initialize the renderer options using the options set in the Scene
        self.set_renderer_options()
        # create the VisualRenderer objects
        self.visual_renderers = [GLVisualRenderer(visual) for visual in self.get_visuals()]
        
    def clear(self):
        """Clear the scene."""
        # clear the buffer (and depth buffer is 3D is activated)
        if self.scene.get('renderer_options', {}).get('activate3D', None):
            gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        else:
            gl.glClear(gl.GL_COLOR_BUFFER_BIT)
        
    def paint(self):
        """Paint the scene."""
        # clear
        self.clear()
        # paint all visual renderers
        for visual_renderer in self.visual_renderers:
            visual_renderer.paint()
        
    def resize(self, width, height):
        """Resize the canvas and make appropriate changes to the scene."""
        # paint within the whole window
        gl.glViewport(0, 0, width, height)

        # compute the constrained viewport
        vx = vy = 1.0
        if height > 0:
            a = float(width) / height
            if a > 1:
                vx = a
            else:
                vy = 1. / a
                
        # update the viewport and window size for all visuals
        for visual in self.get_visuals():
            # get the appropriate viewport, depending on ratio constrain
            if visual.get('constrain_ratio', None):
                viewport = vx, vy
            else:
                viewport = 1, 1
            # update viewport and window_size
            self.set_data(visual,
                          viewport=viewport,
                          window_size=(width, height))
                          
            
if __name__ == '__main__':
    
    from graphscene import GraphScene
    r = GLRenderer(GraphScene)
    
    
    
     
    class GLPlotWidget(QGLWidget):
        def set_renderer(self, renderer):
            self.renderer = renderer
     
        def initializeGL(self):
            self.renderer.initialize()
     
        def paintGL(self):
            self.renderer.paint()
     
        def resizeGL(self, width, height):
            self.renderer.resize(width, height)
 
    # TEST WINDOW
    import sys
    class TestWindow(QtGui.QMainWindow):
        def __init__(self):
            super(TestWindow, self).__init__()
            self.widget = GLPlotWidget()
            self.widget.set_renderer(r)
            self.setGeometry(100, 100, 600, 600)
            self.setCentralWidget(self.widget)
            self.show()
 
    # app = QtGui.QApplication(sys.argv)
    window = TestWindow()
    window.show()
    # app.exec_()
    
    