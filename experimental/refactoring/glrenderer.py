from galry import QtGui, QtCore, QtOpenGL
from galry import log_info
from QtOpenGL import QGLWidget
import OpenGL.GL as gl
import numpy as np

def enforce_dtype(arr, dtype, msg=""):
    """Force the dtype of a Numpy array."""
    if isinstance(arr, np.ndarray):
        if arr.dtype is not np.dtype(dtype):
            log_debug("enforcing dtype for array %s %s" % (str(arr.dtype), msg))
            return np.array(arr, dtype)
    return arr
    
    
    
    

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
        
        
class Uniform(object):# TODO
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


class Texture(object):# TODO
    @staticmethod
    def create():
        pass
        
    @staticmethod
    def bind(buffer):
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
    """Handle vertex and fragment shaders."""
    def __init__(self, vertex_shader, fragment_shader):
        """Compile shaders and create a program."""
        self.vertex_shader = vertex_shader
        self.fragment_shader = fragment_shader
        # compile shaders
        self.compile()
        # create program
        self.program = self.create_program()

    def compile_shader(self, source, shader_type):
        """Compile a shader (vertex or fragment shader).
        
        Arguments:
          * source: the shader source code as a string.
          * shader_type: either gl.GL_VERTEX_SHADER or gl.GL_FRAGMENT_SHADER.
        
        """
        # compile shader
        shader = gl.glCreateShader(shader_type)
        gl.glShaderSource(shader, source)
        gl.glCompileShader(shader)
        
        result = gl.glGetShaderiv(shader, gl.GL_COMPILE_STATUS)
        infolog = gl.glGetShaderInfoLog(shader)
        if infolog:
            infolog = "\n" + infolog
        # check compilation error
        if not(result):
            msg = "Compilation error for %s." % str(shader_type)
            msg += infolog
            msg += source
            raise RuntimeError(msg)
        else:
            log_info("Compilation succeeded for %s.%s" % (str(shader_type), infolog))
        return shader
        
    def compile(self):
        """Compile the shaders."""
        self.vs = self.compile_shader(self.vertex_shader, gl.GL_VERTEX_SHADER)
        self.fs = self.compile_shader(self.fragment_shader, gl.GL_FRAGMENT_SHADER)
        
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
  
    def activate_shaders(self):
        """Activate shaders for the rest of the rendering call."""
        gl.glUseProgram(self.program)
        
    def deactivate_shaders(self):
        """Deactivate shaders for the rest of the rendering call."""
        gl.glUseProgram(0)
        

# Slicing classes
# ---------------
MAX_VBO_SIZE = 65000

class Slicer(object):
    @staticmethod
    def _get_slices(size):
        """Return a list of slices for a given dataset size.
        
        Arguments:
          * size: the size of the dataset, i.e. the number of points.
          
        Returns:
          * slices: a list of pairs `(position, slice_size)` where `position`
            is the position of this slice in the original buffer, and
            `slice_size` the slice size.
        
        """
        maxsize = MAX_VBO_SIZE
        nslices = int(np.ceil(size / float(maxsize)))
        return [(i*maxsize, min(maxsize+1, size-i*maxsize)) for i in xrange(nslices)]

    @staticmethod
    def _slice_bounds(bounds, position, slice_size):
        """Slice data bounds in a *single* slice according to the VBOs slicing.
        
        Arguments:
          * bounds: the bounds as specified by the user in `create_dataset`.
          * position: the position of the current slice.
          * slice_size: the size of the current slice.
        
        Returns:
          * bounds_sliced: the bounds for the current slice. It is a list an
            1D array of integer indices.
        
        TODO: update and make it vectorized? (currently it is called once per
        slice)
        
        """
        # first bound index after the sliced VBO: nothing to paint
        if bounds[0] >= position + slice_size:
            bounds_sliced = None
        # last bound index before the sliced VBO: nothing to paint
        elif bounds[-1] < position:
            bounds_sliced = None
        # the current sliced VBO intersects the bounds: something to paint
        else:
            bounds_sliced = bounds
            # get the bounds that fall within the sliced VBO
            ind = (bounds_sliced>=position) & (bounds_sliced<position + slice_size)
            bounds_sliced = bounds_sliced[ind]
            # remove the onset (first index of the sliced VBO)
            bounds_sliced -= position
            # handle the case when the slice cuts between two bounds
            if not ind[0]:
                bounds_sliced = np.hstack((0, bounds_sliced))
            if not ind[-1]:
                bounds_sliced = np.hstack((bounds_sliced, slice_size))
        return enforce_dtype(bounds_sliced, np.int32)
        
    def set_size(self, size, bounds):
        self.size = size
        self.bounds = bounds
        # compute the data slicing with respect to bounds (specified in the
        # template) and to the maximum size of a VBO.
        self.slice_count = int(np.ceil(self.size / float(MAX_VBO_SIZE)))
        self.slices = self._get_slices(self.size)
        self.subdata_bounds = [self._slice_bounds(self.bounds, pos, size) \
            for pos, size in self.slices]
       
       
class SlicedAttribute(object):
    def __init__(self, slicer, location):
        self.set_slicer(slicer)
        self.location = location
        # create the sliced buffers
        self.create()
        
    def set_slicer(self, slicer):
        """Set the slicer."""
        self.slicer = slicer
        self.slices = self.slicer.slices
        self.size = self.slicer.size
        
    def create(self):
        """Create the sliced buffers."""
        self.attributes = [Attribute.create() for _ in self.slices]
    
    def load(self, data):
        """Load data on all sliced buffers."""
        # NOTE: the slicer needs to be updated if the size of the data changes
        for buffer, (pos, size) in zip(self.attributes, self.slices):
            Attribute.bind(buffer, self.location)
            Attribute.load(data[pos:pos + size,:])

    def bind(self, slice):
        Attribute.bind(self.attributes[slice], self.location)
        

# Painter class
# -------------
class Painter(object):
    """Provides low-level methods for calling OpenGL rendering commands."""
    
    @staticmethod
    def draw_arrays(primtype, offset, size):
        """Render an array of primitives."""
        gl.glDrawArrays(primtype, offset, size)
        
    @staticmethod
    def draw_multi_arrays(bounds):
        """Render several arrays of primitives."""
        first = bounds[:-1]
        count = np.diff(bounds)
        primcount = len(bounds) - 1
        gl.glMultiDrawArrays(gl_primitive_type, first, count, primcount)
        
    @staticmethod
    def draw_indexed_arrays():
        pass# TODO
        
    @staticmethod
    def draw_indexed_multi_arrays():
        pass# TODO


# Visual renderer
# ---------------
class GLVisualRenderer(object):
    """Handle rendering of one visual"""
    
    def __init__(self, visual):
        """Initialize the visual renderer, create the slicer, initialize
        all variables and the shaders."""
        self.visual = visual
        # set the primitive type from its name
        self.primitive_type = getattr(gl, "GL_%s" % self.visual['primitive_type'])
        # set the slicer
        self.slicer = Slicer()
        # get size and bounds
        size = self.visual['size']
        bounds = np.array(self.visual.get('bounds', [0, size]), np.int32)
        self.update_size(size, bounds)
        # compile and link the shaders
        self.shader_manager = ShaderManager(self.visual['vertex_shader'],
                                            self.visual['fragment_shader'])
        # initialize all variables
        self.initialize_variables()
        
    def update_size(self, size, bounds):
        """Update the size of the visual, and update the slicer too."""
        self.size = size
        self.bounds = bounds
        # update the slicer
        self.slicer.set_size(size, bounds)
        # update the slices and sub data bounds (bounds for each slice)
        self.slices = self.slicer.slices
        self.subdata_bounds = self.slicer.subdata_bounds
    
    
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
        pass# TODO
        
    def initialize_uniform(self, name):
        pass# TODO
        
        
    # Loading methods
    # ---------------
    def load_variables(self):
        pass# TODO
        
    def load_attribute(self, name, data):
        pass# TODO
        
    def load_texture(self, name, data):
        pass# TODO
        
    def load_uniform(self, name, data):
        pass# TODO
        
        
    # Updating methods
    # ----------------
    def update_variables(self):
        pass# TODO
        
    def update_attribute(self, name, data):
        pass# TODO
        
    def update_texture(self, name, data):
        pass# TODO
        
    def update_uniform(self, name, data):
        pass# TODO
        
        
    # Binding methods
    # ---------------
    def bind_attributes(self, slice):
        """Bind all attributes of the visual for the given slice.
        This method is used during rendering."""
        attributes = self.get_variables('attribute')
        for variable in attributes:
            Attribute.set_attribute(variable['location'], variable['ndim'])
            variable['sliced_attribute'].bind(slice)
            
    def bind_textures(self, slice):
        """Bind all textures of the visual for the given slice.
        This method is used during rendering."""
        textures = self.get_variables('texture')
        for variable in textures:
            Texture.bind(variable.get('buffer', None))
            
        
    # Paint methods
    # -------------
    def paint(self):
        """Paint the visual slice by slice."""
        # activate the shaders
        self.shader_manager.activate_shaders()
        for slice in xrange(len(self.slices)):
            # get slice bounds
            slice_bounds = self.subdata_bounds[slice]
            # bind all attributes for that slice
            self.bind_attributes(slice)
            # bind all texturex for that slice
            self.bind_textures(slice)
            # call the appropriate OpenGL rendering command
            Painter.draw_arrays(self.primitive_type, slice_bounds[0],  slice_bounds[1] -  slice_bounds[0])
            # TODO: handle multi arrays or indexed arrays
            
        
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
        # TODO
        
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

