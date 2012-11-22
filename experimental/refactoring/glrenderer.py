from galry import QtGui, QtCore, QtOpenGL
from galry import log_info, log_debug, log_warn
from QtOpenGL import QGLWidget
import OpenGL.GL as gl
import numpy as np
import sys


def enforce_dtype(arr, dtype, msg=""):
    """Force the dtype of a Numpy array."""
    if isinstance(arr, np.ndarray):
        if arr.dtype is not np.dtype(dtype):
            log_debug("enforcing dtype for array %s %s" % (str(arr.dtype), msg))
            return np.array(arr, dtype)
    return arr
    
def get_application():
    """Get the current QApplication, or create a new one."""
    app_created = False
    app = QtCore.QCoreApplication.instance()
    if app is None:
        log_debug("creating a new QApplication in order to show the window")
        app = QtGui.QApplication(sys.argv)
        app_created = True
    return app, app_created
    
def show_window(window, **kwargs):
    """Create a QT window in Python, or interactively in IPython with QT GUI
    event loop integration:
    
        # in ~/.ipython/ipython_config.py
        c.TerminalIPythonApp.gui = 'qt'
        c.TerminalIPythonApp.pylab = 'qt'
    
    See also:
        http://ipython.org/ipython-doc/dev/interactive/qtconsole.html#qt-and-the-qtconsole
    
    """
    app, app_created = get_application()
    app.references = set()
    if not isinstance(window, QtGui.QWidget):
        window = window(**kwargs)
    app.references.add(window)
    window.show()
    if app_created:
        app.exec_()
    return window
    
    
class GLVersion(object):
    # self.version_header = '#version 120'
    # self.precision_header = 'precision mediump float;'
    @staticmethod
    def get_renderer_info():
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
    
    @staticmethod
    def version_header():
        return '#version 120'
        
    @staticmethod
    def precision_header():
        if GLVersion.get_renderer_info()['glsl_version'] >= '1.3':
            return 'precision mediump float;'
        else:
            return ''
    
    
# Low-level OpenGL functions to initialize/load variables
# -------------------------------------------------------
class Attribute(object):
    @staticmethod
    def create():
        """Create a new buffer and return a `buffer` index."""
        return gl.glGenBuffers(1)
        
    @staticmethod
    def bind(buffer, location=None, index=False):
        """Bind a buffer and associate a given location."""
        if not index:
            gltype = gl.GL_ARRAY_BUFFER
        else:
            gltype = gl.GL_ELEMENT_ARRAY_BUFFER
        if location >= 0:
            gl.glEnableVertexAttribArray(location)
        gl.glBindBuffer(gltype, buffer)
        
    @staticmethod
    def set_attribute(location, ndim):
        """Specify the type of the attribute before rendering."""
        gl.glVertexAttribPointer(location, ndim, gl.GL_FLOAT, gl.GL_FALSE, 0, None)
    
    @staticmethod
    def convert_data(data):
        """Force 32-bit floating point numbers for data."""
        return enforce_dtype(data, np.float32)
    
    @staticmethod
    def load(data, index=False):
        """Load data in the buffer for the first time. The buffer must
        have been bound before."""
        if not index:
            gltype = gl.GL_ARRAY_BUFFER
            data = Attribute.convert_data(data)
        else:
            gltype = gl.GL_ELEMENT_ARRAY_BUFFER
        gl.glBufferData(gltype, data, gl.GL_DYNAMIC_DRAW)
        
    @staticmethod
    def update(data, onset=0):
        """Update data in the currently bound buffer."""
        data = Attribute.convert_data(data)
        # convert onset into bytes count
        onset *= data.shape[1] * data.itemsize
        gl.glBufferSubData(gl.GL_ARRAY_BUFFER, int(onset), data)
    
    @staticmethod
    def delete(*buffers):
        """Delete buffers."""
        gl.glDeleteBuffers(len(buffers), buffers)
        
        
class Uniform(object):
    float_suffix = {True: 'f', False: 'i'}
    array_suffix = {True: 'v', False: ''}
    # glUniform[Matrix]D[f][v]
    
    @staticmethod
    def convert_data(data):
        return enforce_dtype(data, np.float32)
    
    @staticmethod
    def load_scalar(location, data):
        is_float = type(data) == float
        funname = 'glUniform1%s' % Uniform.float_suffix[is_float]
        getattr(gl, funname)(location, data)

    @staticmethod
    def load_vector(location, data):
        is_float = type(data[0]) == float
        ndim = len(data)
        funname = 'glUniform%d%s' % (ndim, Uniform.float_suffix[is_float])
        getattr(gl, funname)(location, *data)
    
    @staticmethod
    def load_array(location, data):
        data = Attribute.convert_data(data)
        is_float = (data.dtype == np.float32)
        size, ndim = data.shape
        funname = 'glUniform%d%sv' % (ndim, Uniform.float_suffix[is_float])
        getattr(gl, funname)(location, size, data)
        
    @staticmethod
    def load_matrix(location, data):
        data = Attribute.convert_data(data)
        is_float = (data.dtype == np.float32)
        n, m = data.shape
        # TODO: arrays of matrices?
        funname = 'glUniformMatrix%dx%d%sv' % (n, m, Uniform.float_suffix[is_float])
        getattr(gl, funname)(location, 1, False, data)
        

class Texture(object):
    @staticmethod
    def create(ndim):
        """Create a texture with the specifyed number of dimensions."""
        buffer = gl.glGenTextures(1)
        gl.glPixelStorei(gl.GL_UNPACK_ALIGNMENT, 1)
        Texture.bind(buffer, ndim)
        textype = getattr(gl, "GL_TEXTURE_%dD" % ndim)
        gl.glTexParameteri(textype, gl.GL_TEXTURE_WRAP_S, gl.GL_CLAMP)
        gl.glTexParameteri(textype, gl.GL_TEXTURE_WRAP_T, gl.GL_CLAMP)
        gl.glTexParameteri(textype, gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST)
        gl.glTexParameteri(textype, gl.GL_TEXTURE_MIN_FILTER, gl.GL_NEAREST)
        return buffer
        
    @staticmethod
    def bind(buffer, ndim):
        """Bind a texture buffer."""
        textype = getattr(gl, "GL_TEXTURE_%dD" % ndim)
        gl.glBindTexture(textype, buffer)
    
    @staticmethod
    def get_info(data):
        """Return information about texture data."""
        # find shape, ndim, ncomponents
        shape = data.shape
        if shape[0] == 1:
            ndim = 1
        elif shape[0] > 1:
            ndim = 2
        ncomponents = shape[2]
        # ncomponents==1 ==> GL_R, 3 ==> GL_RGB, 4 ==> GL_RGBA
        component_type = getattr(gl, ["GL_INTENSITY8", None, "GL_RGB", "GL_RGBA"] \
                                            [ncomponents - 1])
        return ndim, ncomponents, component_type

    @staticmethod    
    def convert_data(data):
        """convert data in a array of uint8 in [0, 255]."""
        return np.array(255 * data, dtype=np.uint8)
    
    @staticmethod
    def load(data):
        """Load texture data in a bound texture buffer."""
        # convert data in a array of uint8 in [0, 255]
        data = Texture.convert_data(data)
        shape = data.shape
        # get texture info
        ndim, ncomponents, component_type = Texture.get_info(data)
        textype = getattr(gl, "GL_TEXTURE_%dD" % ndim)
        # load data in the buffer
        if ndim == 1:
            gl.glTexImage1D(textype, 0, component_type, shape[1], 0, component_type,
                            gl.GL_UNSIGNED_BYTE, data)
        elif ndim == 2:
            gl.glTexImage2D(textype, 0, component_type, shape[0], shape[1], 0,
                            component_type, gl.GL_UNSIGNED_BYTE, data)
        
    @staticmethod
    def update(data):
        """Update a texture."""
        # convert data in a array of uint8 in [0, 255]
        data = Texture.convert_data(data)
        shape = data.shape
        # get texture info
        ndim, ncomponents, component_type = Texture.get_info(data)
        textype = getattr(gl, "GL_TEXTURE_%dD" % ndim)
        # update buffer
        if ndim == 1:
            gl.glTexSubImage1D(textype, 0, 0, shape[1],
                               component_type, gl.GL_UNSIGNED_BYTE, data)
        elif ndim == 2:
            gl.glTexSubImage2D(textype, 0, 0, 0, shape[0], shape[1],
                               component_type, gl.GL_UNSIGNED_BYTE, data)

    @staticmethod
    def delete(*buffers):
        """Delete texture buffers."""
        gl.glDeleteTextures(buffers)

        
# Shader manager
# --------------
class ShaderManager(object):
    """Handle vertex and fragment shaders."""
    def __init__(self, vertex_shader, fragment_shader):
        """Compile shaders and create a program."""
        # add headers
        vertex_shader = GLVersion.version_header() + vertex_shader
        fragment_shader = GLVersion.version_header() + fragment_shader
        # set shader source
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
            infolog = "\n" + infolog.strip()
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
        
    def get_attribute_location(self, name):
        """Return the location of an attribute after the shaders have compiled."""
        return gl.glGetAttribLocation(self.program, name)
  
    def get_uniform_location(self, name):
        """Return the location of a uniform after the shaders have compiled."""
        return gl.glGetUniformLocation(self.program, name)
  
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
    def _get_slices(size, maxsize=None):
        """Return a list of slices for a given dataset size.
        
        Arguments:
          * size: the size of the dataset, i.e. the number of points.
          
        Returns:
          * slices: a list of pairs `(position, slice_size)` where `position`
            is the position of this slice in the original buffer, and
            `slice_size` the slice size.
        
        """
        if maxsize is None:
            maxsize = MAX_VBO_SIZE
        if maxsize > 0:
            nslices = int(np.ceil(size / float(maxsize)))
        else:
            nslices = 0
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
        
    def set_size(self, size, bounds=None, doslice=True):
        """Update the total size of the buffer and/or the bounds, and update
        the slice information accordingly."""
        if bounds is None:
            bounds = np.array([0, size], dtype=np.int32)
        # deactivate slicing by using a maxsize number larger than the
        # actual size
        if doslice:
            maxsize = 2 * size
        else:
            maxsize = None
        self.size = size
        self.bounds = bounds
        # compute the data slicing with respect to bounds (specified in the
        # template) and to the maximum size of a VBO.
        self.slices = self._get_slices(self.size, maxsize)
        self.slice_count = len(self.slices)
        self.subdata_bounds = [self._slice_bounds(self.bounds, pos, size) \
            for pos, size in self.slices]
       
       
class SlicedAttribute(object):
    def __init__(self, slicer, location):
        # self.set_slicer(slicer)
        self.slicer = slicer
        self.location = location
        # create the sliced buffers
        self.create()
        
    # def set_slicer(self, slicer):
        # """Set the slicer."""
        
    def create(self):
        """Create the sliced buffers."""
        self.buffers = [Attribute.create() for _ in self.slicer.slices]
    
    def delete_buffers(self):
        """Delete all sub-buffers."""
        # for buffer in self.buffers:
        Attribute.delete(*self.buffers)
    
    def load(self, data):
        """Load data on all sliced buffers."""
        for buffer, (pos, size) in zip(self.buffers, self.slicer.slices):
            Attribute.bind(buffer, self.location)
            Attribute.load(data[pos:pos + size,:])

    def bind(self, slice=None):
        if slice is None:
            slice = 0
        Attribute.bind(self.buffers[slice], self.location)
        
    def update(self, data, mask=None):
        """Update data on all sliced buffers."""
        # NOTE: the slicer needs to be updated if the size of the data changes
        # default mask
        if mask is None:
            mask = np.ones(self.slicer.size, dtype=np.bool)
        # is the current subVBO within the given [onset, offset]?
        within = False
        # update VBOs
        for buffer, (pos, size) in zip(self.buffers, self.slicer.slices):
            subdata = data[pos:pos + size,:]
            submask = mask[pos:pos + size]
            # if there is at least one True in the slice mask (submask)
            if submask.any():
                # this sub-buffer contains updated indices
                subonset = submask.argmax()
                suboffset = len(submask) - 1 - submask[::-1].argmax()
                Attribute.bind(buffer, self.location)
                Attribute.update(subdata[subonset:suboffset + 1, :], subonset)

    
# Painter class
# -------------
class Painter(object):
    """Provides low-level methods for calling OpenGL rendering commands."""
    
    @staticmethod
    def draw_arrays(primtype, offset, size):
        """Render an array of primitives."""
        gl.glDrawArrays(primtype, offset, size)
        
    @staticmethod
    def draw_multi_arrays(primtype, bounds):
        """Render several arrays of primitives."""
        first = bounds[:-1]
        count = np.diff(bounds)
        primcount = len(bounds) - 1
        gl.glMultiDrawArrays(primtype, first, count, primcount)
        
    @staticmethod
    def draw_indexed_arrays(primtype, size):
        gl.glDrawElements(primtype, size, gl.GL_UNSIGNED_INT, None)


# Visual renderer
# ---------------
class GLVisualRenderer(object):
    """Handle rendering of one visual"""
    
    # hold all data changes until the next rendering pass happens
    data_updating = {}
    
    def __init__(self, visual):
        """Initialize the visual renderer, create the slicer, initialize
        all variables and the shaders."""
        self.visual = visual
        # set the primitive type from its name
        self.set_primitive_type(self.visual['primitive_type'])
        # set the slicer
        self.slicer = Slicer()
        # used when slicing needs to be deactivated (like for indexed arrays)
        self.noslicer = Slicer()
        # get size and bounds
        size = self.visual['size']
        bounds = np.array(self.visual.get('bounds', [0, size]), np.int32)
        # self.update_size(size, bounds)
        self.slicer.set_size(size, bounds)
        self.noslicer.set_size(size, bounds, doslice=False)
        # compile and link the shaders
        self.shader_manager = ShaderManager(self.visual['vertex_shader'],
                                            self.visual['fragment_shader'])
        # initialize all variables
        self.initialize_variables()
        self.load_variables()
        
    def set_primitive_type(self, primtype):
        # set the primitive type from its name
        self.primitive_type = getattr(gl, "GL_%s" % primtype)
    
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
            return None
            # raise ValueError("The variable %s has not been found" % name)
        return variables[0]
        
        
    # Initialization methods
    # ----------------------
    def initialize_variables(self):
        """Initialize all variables, after the shaders have compiled."""
        # find out whether indexing is used or not, because in this case
        # the slicing needs to be deactivated
        if self.get_variables('index'):
            # deactivate slicing
            self.slicer = self.noslicer
            log_info("deactivating slicing")
            self.use_index = True
        else:
            self.use_index = False
        # initialize all variables
        for var in self.get_variables():
            shader_type = var['shader_type']
            name = var['name']
            # call initialize_***(name) to initialize that variable
            getattr(self, 'initialize_%s' % shader_type)(name)
        # special case for uniforms: need to load them the first time
        uniforms = self.get_variables('uniform')
        self.set_data(**dict([(v['name'], v['data']) for v in uniforms]))
    
    def initialize_attribute(self, name):
        """Initialize an attribute: get the shader location, create the
        sliced buffers, and load the data."""
        # retrieve the location of that attribute in the shader
        location = self.shader_manager.get_attribute_location(name)
        variable = self.get_variable(name)
        variable['location'] = location
        # initialize the sliced buffers
        variable['sliced_attribute'] = SlicedAttribute(self.slicer, location)
        
    def initialize_index(self, name):
        variable = self.get_variable(name)
        variable['buffer'] = Attribute.create()
        
    def initialize_texture(self, name):
        variable = self.get_variable(name)
        variable['buffer'] = Texture.create(variable['ndim'])
        
    def initialize_uniform(self, name):
        """Initialize an uniform: get the location after the shaders have
        been compiled."""
        location = self.shader_manager.get_uniform_location(name)
        variable = self.get_variable(name)
        variable['location'] = location
        
        
    # Loading methods
    # ---------------
    def load_variables(self):
        """Load data for all variables at initialization."""
        for var in self.get_variables():
            shader_type = var['shader_type']
            # skip uniforms
            if shader_type == 'uniform':
                continue
            # call load_***(name) to load that variable
            getattr(self, 'load_%s' % shader_type)(var['name'])
        
    def load_attribute(self, name, data=None):
        """Load data for an attribute variable."""
        variable = self.get_variable(name)
        if data is None:
            data = variable.get('data', None)
        if data is not None:
            variable['sliced_attribute'].load(data)
        
    def load_index(self, name, data=None):
        """Load data for an index variable."""
        variable = self.get_variable(name)
        if data is None:
            data = variable.get('data', None)
        if data is not None:
            Attribute.bind(variable['buffer'], index=True)
            Attribute.load(data, index=True)
        
    def load_texture(self, name, data=None):
        """Load data for a texture variable."""
        variable = self.get_variable(name)
        if data is None:
            data = variable.get('data', None)
        if data is not None:
            Texture.bind(variable['buffer'], variable['ndim'])
            Texture.load(data)
        
    def load_uniform(self, name, data=None):
        """Load data for an uniform variable."""
        variable = self.get_variable(name)
        location = variable['location']
        if data is None:
            data = variable.get('data', None)
        if data is not None:
            ndim = variable['ndim']
            size = variable.get('size', None)
            # one value
            if not size:
                # scalar or vector
                if type(ndim) == int or type(ndim) == long:
                    if ndim == 1:
                        Uniform.load_scalar(location, data)
                    else:
                        Uniform.load_vector(location, data)
                # matrix 
                elif type(ndim) == tuple:
                    Uniform.load_matrix(location, data)
            # array
            else:
                # scalar or vector
                if type(ndim) == int or type(ndim) == long:
                    Uniform.load_array(location, data)
                    
            
    # Updating methods
    # ----------------
    def update_variable(self, name, data, **kwargs):
        """Update data of a variable."""
        variable = self.get_variable(name)
        if variable is None:
            log_info("Variable '%s' was not found, unable to update it." % name)
        else:
            shader_type = variable['shader_type']
            getattr(self, 'update_%s' % shader_type)(name, data, **kwargs)
    
    def update_attribute(self, name, data, bounds=None):
        """Update data for an attribute variable."""
        variable = self.get_variable(name)
        variable['data'] = data
        # handle size changing
        if data.shape[0] != self.slicer.size:
            # update the slicer size and bounds
            self.slicer.set_size(data.shape[0], bounds, doslice=not(self.use_index))
            # delete old buffers
            variable['sliced_attribute'].delete_buffers()
            # create new buffers
            variable['sliced_attribute'].create()
            # load data
            variable['sliced_attribute'].load(data)
        else:
            # update data
            variable['sliced_attribute'].update(data)
        
    def update_texture(self, name, data):
        """Update data for a texture variable."""
        variable = self.get_variable(name)
        prevshape = variable['data'].shape
        variable['data'] = data
        # handle size changing
        if data.shape != prevshape:
            # delete old buffers
            Texture.delete(variable['buffer'])
            variable['ndim'], variable['ncomponents'], _ = Texture.get_info(data)
            # create new buffer
            variable['buffer'] = Texture.create(variable['ndim'])
            # load data
            Texture.bind(variable['buffer'], variable['ndim'])
            Texture.load(data)
        else:
            # update data
            Texture.bind(variable['buffer'], variable['ndim'])
            Texture.update(data)
        
    def update_uniform(self, name, data):
        """Update data for an uniform variable."""
        variable = self.get_variable(name)
        variable['data'] = data
        # the uniform interface is the same for load/update
        self.load_uniform(name, data)
        
    def set_data(self, **kwargs):
        """Load data for the specified visual. Uploading does not happen here
        but in `update_all_variables` instead, since this needs to happen
        after shader program binding in the paint method.
        
        Arguments:
          * **kwargs: the data to update as name:value pairs. name can be
            any field of the visual, plus one of the following keywords:
              * size: the size of the visual,
              * primitive_type: the GL primitive type,
              * constrain_ratio: whether to constrain the ratio of the visual,
              * constrain_navigation: whether to constrain the navigation,
        
        """
        # we register the data changes here so that they can be actually be
        # done later, in update_all_variables
        
        # handle size and bounds keyword
        size = kwargs.pop('size', None)
        bounds = kwargs.pop('bounds', None)
        if size is not None or bounds is not None:
            self.slicer.set_size(size, bounds)
        
        # handle primitive type special keyword
        primitive_type = kwargs.pop('primitive_type', None)
        if primitive_type is not None:
            self.visual['primitive_type'] = primitive_type
            self.set_primitive_type(primitive_type)
        
        # handle constrain_ratio keyword
        constrain_ratio = kwargs.pop('constrain_ratio', None)
        if constrain_ratio is not None:
            self.visual['constrain_ratio'] = constrain_ratio
        
        # handle constrain_navigation keyword
        constrain_navigation = kwargs.pop('constrain_navigation', None)
        if constrain_navigation is not None:
            self.visual['constrain_navigation'] = constrain_navigation
        
        # flag the other variables as to be updated
        self.data_updating.update(**kwargs)
        
    def update_all_variables(self):
        """Upload all new data that needs to be updated."""
        # go through all data changes
        for name, data in self.data_updating.iteritems():
            # log_info("Updating variable '%s'" % name)
            self.update_variable(name, data)
        # reset the data updating dictionary
        self.data_updating.clear()
        
        
    # Binding methods
    # ---------------
    def bind_attributes(self, slice=None):
        """Bind all attributes of the visual for the given slice.
        This method is used during rendering."""
        attributes = self.get_variables('attribute')
        for variable in attributes:
            Attribute.set_attribute(variable['location'], variable['ndim'])
            variable['sliced_attribute'].bind(slice)
            
    def bind_indices(self):
        indices = self.get_variables('index')
        for variable in indices:
            Attribute.bind(variable['buffer'], index=True)
            
    def bind_textures(self):
        """Bind all textures of the visual.
        This method is used during rendering."""
        textures = self.get_variables('texture')
        for variable in textures:
            buffer = variable.get('buffer', None)
            if buffer is not None:
                Texture.bind(buffer, variable['ndim'])
            else:
                log_info("Texture '%s' was not propertly initialized." % \
                         variable['name'])


    # Paint methods
    # -------------
    def paint(self):
        """Paint the visual slice by slice."""
        # activate the shaders
        self.shader_manager.activate_shaders()
        # update all variables
        self.update_all_variables()
        # bind all texturex for that slice
        self.bind_textures()
        
        if self.use_index:
            self.bind_attributes()
            self.bind_indices()
            Painter.draw_indexed_arrays(self.primitive_type, self.slicer.size)
        else:
            # draw all sliced buffers
            for slice in xrange(len(self.slicer.slices)):
                # get slice bounds
                slice_bounds = self.slicer.subdata_bounds[slice]
                # bind all attributes for that slice
                self.bind_attributes(slice)
                # call the appropriate OpenGL rendering command
                # if len(self.slicer.bounds) <= 2:
                if len(slice_bounds) <= 2:
                    Painter.draw_arrays(self.primitive_type, slice_bounds[0],  slice_bounds[1] -  slice_bounds[0])
                else:
                    Painter.draw_multi_arrays(self.primitive_type, slice_bounds)
            
        
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
        self.initialized = False
    
    # def get_renderer_info(self):
        # """Return information about the client renderer.
        
        # Arguments:
          # * info: a dictionary with the following keys:
              # * renderer_name
              # * opengl_version
              # * glsl_version
              
        # """
        # return {
            # 'renderer_name': gl.glGetString(gl.GL_RENDERER),
            # 'opengl_version': gl.glGetString(gl.GL_VERSION),
            # 'glsl_version': gl.glGetString(gl.GL_SHADING_LANGUAGE_VERSION)
        # }
    
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
        """Load data for the specified visual. Uploading does not happen here
        but in `update_all_variables` instead, since this needs to happen
        after shader program binding in the paint method.
        
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
        if type(visual) == dict:
            visual = visual['name']
        # call set_data on the given visual renderer
        self.visual_renderers[visual].set_data(**kwargs)
        
        
    # Rendering methods
    # -----------------
    def initialize(self):
        """Initialize the renderer."""
        # print the renderer information
        for key, value in GLVersion.get_renderer_info().iteritems():
            log_info(key + ": " + value)
        # initialize the renderer options using the options set in the Scene
        self.set_renderer_options()
        # create the VisualRenderer objects
        self.visual_renderers = dict([(visual['name'], GLVisualRenderer(visual)) for visual in self.get_visuals()])
        
    def clear(self):
        """Clear the scene."""
        # clear the buffer (and depth buffer is 3D is activated)
        if self.scene.get('renderer_options', {}).get('activate3D', None):
            gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        else:
            gl.glClear(gl.GL_COLOR_BUFFER_BIT)
        
    def paint(self):
        """Paint the scene."""
        # self.initialized = True
        # clear
        self.clear()
        # paint all visual renderers
        for name, visual_renderer in self.visual_renderers.iteritems():
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
                viewport = 1., 1.
            # update viewport and window_size
            self.set_data(visual,
                          viewport=viewport,
                          window_size=(width, height))
                          

def show_visual(visual):
    visual['name'] = 'visual'
    scene = {'visuals': [visual]}
    show_scene(scene)
                          
def show_scene(scene):
    r = GLRenderer(scene)
    
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
    class TestWindow(QtGui.QMainWindow):
        def __init__(self):
            super(TestWindow, self).__init__()
            self.widget = GLPlotWidget()
            self.widget.set_renderer(r)
            self.setGeometry(100, 100, 600, 600)
            self.setCentralWidget(self.widget)
            self.show()

    show_window(TestWindow)
                          
if __name__ == '__main__':
    
    from graphscene import GraphScene
    show_scene(GraphScene)
    
    