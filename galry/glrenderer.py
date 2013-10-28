try:
    import OpenGL.GL as gl
except:
    from galry import log_warn
    log_warn(("PyOpenGL is not available and Galry won't be"
        " able to render plots."))
    class _gl(object):
        def mock(*args, **kwargs):
            return None
        def __getattr__(self, name):
            return self.mock
    gl = _gl()
from collections import OrderedDict
import numpy as np
import sys
from galry import enforce_dtype, DataNormalizer, log_info, log_debug, \
    log_warn, RefVar

    
__all__ = ['GLVersion', 'GLRenderer']
    
    
# GLVersion class
# ---------------
class GLVersion(object):
    """Methods related to the GL version."""
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
        if GLVersion.get_renderer_info()['opengl_version'][0:3] < '2.1':
            return '#version 110\n'
        else:
            return '#version 120\n'
        
    @staticmethod
    def precision_header():
        if GLVersion.get_renderer_info()['glsl_version'] >= '1.3':
            return 'precision mediump float;'
        else:
            return ''
    
    
# Low-level OpenGL functions to initialize/load variables
# -------------------------------------------------------
class Attribute(object):
    """Contains OpenGL functions related to attributes."""
    @staticmethod
    def create():
        """Create a new buffer and return a `buffer` index."""
        return gl.glGenBuffers(1)
    
    @staticmethod
    def get_gltype(index=False):
        if not index:
            return gl.GL_ARRAY_BUFFER
        else:
            return gl.GL_ELEMENT_ARRAY_BUFFER
        
    @staticmethod
    def bind(buffer, location=None, index=False):
        """Bind a buffer and associate a given location."""
        gltype = Attribute.get_gltype(index)
        gl.glBindBuffer(gltype, buffer)
        if location >= 0:
            gl.glEnableVertexAttribArray(location)
        
    @staticmethod
    def set_attribute(location, ndim):
        """Specify the type of the attribute before rendering."""
        gl.glVertexAttribPointer(location, ndim, gl.GL_FLOAT, gl.GL_FALSE, 0, None)
    
    @staticmethod
    def convert_data(data, index=False):
        """Force 32-bit floating point numbers for data."""
        if not index:
            return enforce_dtype(data, np.float32)
        else:
            return np.array(data, np.int32)
        
    
    @staticmethod
    def load(data, index=False):
        """Load data in the buffer for the first time. The buffer must
        have been bound before."""
        data = Attribute.convert_data(data, index=index)
        gltype = Attribute.get_gltype(index)
        gl.glBufferData(gltype, data, gl.GL_DYNAMIC_DRAW)
        
    @staticmethod
    def update(data, onset=0, index=False):
        """Update data in the currently bound buffer."""
        gltype = Attribute.get_gltype(index)
        data = Attribute.convert_data(data, index=index)
        # convert onset into bytes count
        if data.ndim == 1:
            ndim = 1
        elif data.ndim == 2:
            ndim = data.shape[1]
        onset *= ndim * data.itemsize
        gl.glBufferSubData(gltype, int(onset), data)
    
    @staticmethod
    def delete(*buffers):
        """Delete buffers."""
        if buffers:
            gl.glDeleteBuffers(len(buffers), buffers)
        
        
class Uniform(object):
    """Contains OpenGL functions related to uniforms."""
    float_suffix = {True: 'f', False: 'i'}
    array_suffix = {True: 'v', False: ''}
    # glUniform[Matrix]D[f][v]
    
    @staticmethod
    def convert_data(data):
        if isinstance(data, np.ndarray):
            data = enforce_dtype(data, np.float32)
        if type(data) == np.float64:
            data = np.float32(data)
        if type(data) == np.int64:
            data = np.int32(data)
        if type(data) == list:
            data = map(Uniform.convert_data, data)
        if type(data) == tuple:
            data = tuple(map(Uniform.convert_data, data))
        return data
    
    @staticmethod
    def load_scalar(location, data):
        data = Uniform.convert_data(data)
        is_float = (type(data) == float) or (type(data) == np.float32)
        funname = 'glUniform1%s' % Uniform.float_suffix[is_float]
        getattr(gl, funname)(location, data)

    @staticmethod
    def load_vector(location, data):
        if len(data) > 0:
            data = Uniform.convert_data(data)
            is_float = (type(data[0]) == float) or (type(data[0]) == np.float32)
            ndim = len(data)
            funname = 'glUniform%d%s' % (ndim, Uniform.float_suffix[is_float])
            getattr(gl, funname)(location, *data)
    
    @staticmethod
    def load_array(location, data):
        data = Uniform.convert_data(data)
        is_float = (data.dtype == np.float32)
        size, ndim = data.shape
        funname = 'glUniform%d%sv' % (ndim, Uniform.float_suffix[is_float])
        getattr(gl, funname)(location, size, data)
        
    @staticmethod
    def load_matrix(location, data):
        data = Uniform.convert_data(data)
        is_float = (data.dtype == np.float32)
        n, m = data.shape
        # TODO: arrays of matrices?
        if n == m:
            funname = 'glUniformMatrix%d%sv' % (n, Uniform.float_suffix[is_float])
        else:
            funname = 'glUniformMatrix%dx%d%sv' % (n, m, Uniform.float_suffix[is_float])
        getattr(gl, funname)(location, 1, False, data)


class Texture(object):
    """Contains OpenGL functions related to textures."""
    @staticmethod
    def create(ndim=2, mipmap=False, minfilter=None, magfilter=None):
        """Create a texture with the specifyed number of dimensions."""
        buffer = gl.glGenTextures(1)
        gl.glPixelStorei(gl.GL_UNPACK_ALIGNMENT, 1)
        Texture.bind(buffer, ndim)
        textype = getattr(gl, "GL_TEXTURE_%dD" % ndim)
        gl.glTexParameteri(textype, gl.GL_TEXTURE_WRAP_S, gl.GL_CLAMP)
        gl.glTexParameteri(textype, gl.GL_TEXTURE_WRAP_T, gl.GL_CLAMP)
        
        if mipmap:
            if hasattr(gl, 'glGenerateMipmap'):
                gl.glGenerateMipmap(textype)
            else:
                minfilter = 'NEAREST'
                magfilter = 'NEAREST'
            
        if minfilter is None:
            minfilter = 'NEAREST'
        if magfilter is None:
            magfilter = 'NEAREST'
            
        minfilter = getattr(gl, 'GL_' + minfilter)
        magfilter = getattr(gl, 'GL_' + magfilter)
            
        gl.glTexParameteri(textype, gl.GL_TEXTURE_MIN_FILTER, minfilter)
        gl.glTexParameteri(textype, gl.GL_TEXTURE_MAG_FILTER, magfilter)
        
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
        # ndim = 2
        ncomponents = shape[2]
        # ncomponents==1 ==> GL_R, 3 ==> GL_RGB, 4 ==> GL_RGBA
        component_type = getattr(gl, ["GL_INTENSITY8", None, "GL_RGB", "GL_RGBA"] \
                                            [ncomponents - 1])
        return ndim, ncomponents, component_type

    @staticmethod    
    def convert_data(data):
        """convert data in a array of uint8 in [0, 255]."""
        if data.dtype == np.float32 or data.dtype == np.float64:
            return np.array(255 * data, dtype=np.uint8)
        elif data.dtype == np.uint8:
            return data
        else:
            raise ValueError("The texture is in an unsupported format.")
    
    @staticmethod
    def copy(fbo, tex_src, tex_dst, width, height):
        
        # /// bind the FBO
        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, fbo)
        # /// attach the source texture to the fbo
        gl.glFramebufferTexture2D(gl.GL_FRAMEBUFFER, gl.GL_COLOR_ATTACHMENT0,
                                gl.GL_TEXTURE_2D, tex_src, 0)
        # /// bind the destination texture
        gl.glBindTexture(gl.GL_TEXTURE_2D, tex_dst)
        # /// copy from framebuffer (here, the FBO!) to the bound texture
        gl.glCopyTexSubImage2D(gl.GL_TEXTURE_2D, 0, 0, 0, 0, 0, width, height)
        # /// unbind the FBO
        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, 0)
        
        # # ncomponents==1 ==> GL_R, 3 ==> GL_RGB, 4 ==> GL_RGBA
        # component_type = getattr(gl, ["GL_INTENSITY8", None, "GL_RGB", "GL_RGBA"] \
                                            # [ncomponents - 1])
        # gl.glCopyTexImage2D(gl.GL_TEXTURE_2D,
            # 0,  # level
            # component_type, 
            # 0, 0,  # x, y offsets
            # 0, 0,  # x, y
            # w, h, # width, height
            # 0  # border
            # )
            
    # @staticmethod
    # def read_buffer(index=0):
        # gl.glReadBuffer(getattr(gl, 'GL_COLOR_ATTACHMENT%d' % index))
            
    # @staticmethod
    # def draw_buffer():
        # gl.glDrawBuffer(gl.GL_FRONT)
            
    @staticmethod
    def load(data):
        """Load texture data in a bound texture buffer."""
        # convert data in a array of uint8 in [0, 255]
        data = Texture.convert_data(data)
        shape = data.shape
        # get texture info
        ndim, ncomponents, component_type = Texture.get_info(data)
        textype = getattr(gl, "GL_TEXTURE_%dD" % ndim)
        # print ndim, shape, data.shape
        # load data in the buffer
        if ndim == 1:
            gl.glTexImage1D(textype, 0, component_type, shape[1], 0, component_type,
                            gl.GL_UNSIGNED_BYTE, data)
        elif ndim == 2:
            # width, height == shape[1], shape[0]: Thanks to the Confusion Club
            gl.glTexImage2D(textype, 0, component_type, shape[1], shape[0], 0,
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
            gl.glTexSubImage2D(textype, 0, 0, 0, shape[1], shape[0],
                               component_type, gl.GL_UNSIGNED_BYTE, data)

    @staticmethod
    def delete(*buffers):
        """Delete texture buffers."""
        gl.glDeleteTextures(buffers)


class FrameBuffer(object):
    """Contains OpenGL functions related to FBO."""
    @staticmethod
    def create():
        """Create a FBO."""
        if hasattr(gl, 'glGenFramebuffers') and gl.glGenFramebuffers:
            buffer = gl.glGenFramebuffers(1)
        else:
            buffer = None
        return buffer
        
    @staticmethod
    def bind(buffer=None):
        """Bind a FBO."""
        if buffer is None:
            buffer = 0
        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, buffer)
        
    @staticmethod
    def bind_texture(texture, i=0):
        gl.glFramebufferTexture2D(gl.GL_FRAMEBUFFER,
            getattr(gl, 'GL_COLOR_ATTACHMENT%d' % i),
            gl.GL_TEXTURE_2D, texture, 0)

    @staticmethod
    def draw_buffers(n):
        gl.glDrawBuffers([getattr(gl, 'GL_COLOR_ATTACHMENT%d' % i) for i in xrange(n)])
            
    @staticmethod
    def unbind():
        """Unbind a FBO."""
        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, 0)

        
# Shader manager
# --------------
class ShaderManager(object):
    """Handle vertex and fragment shaders.
    
    TODO: integrate in the renderer the shader code creation module.
    
    """
    
    # Initialization methods
    # ----------------------
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
        if not(result) and infolog:
            msg = "Compilation error for %s." % str(shader_type)
            if infolog is not None:
                msg += infolog
            msg += source
            raise RuntimeError(msg)
        else:
            log_debug("Compilation succeeded for %s.%s" % (str(shader_type), infolog))
        return shader
        
    def compile(self):
        """Compile the shaders."""
        # print self.vertex_shader
        # print self.fragment_shader
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
            info = gl.glGetProgramInfoLog(program)
            if info:
                msg += info
                raise RuntimeError(msg)
        
        self.program = program
        return program
        
    def get_attribute_location(self, name):
        """Return the location of an attribute after the shaders have compiled."""
        return gl.glGetAttribLocation(self.program, name)
  
    def get_uniform_location(self, name):
        """Return the location of a uniform after the shaders have compiled."""
        return gl.glGetUniformLocation(self.program, name)
  
  
    # Activation methods
    # ------------------
    def activate_shaders(self):
        """Activate shaders for the rest of the rendering call."""
        # try:
        gl.glUseProgram(self.program)
            # return True
        # except Exception as e:
            # log_info("Error while activating the shaders: " + e.message)
            # return False
        
    def deactivate_shaders(self):
        """Deactivate shaders for the rest of the rendering call."""
        # try:
        gl.glUseProgram(0)
            # return True
        # except Exception as e:
            # log_info("Error while activating the shaders: " + e.message)
            # return True
        
        
    # Cleanup methods
    # ---------------
    def detach_shaders(self):
        """Detach shaders from the program."""
        if gl.glIsProgram(self.program):
            gl.glDetachShader(self.program, self.vs)
            gl.glDetachShader(self.program, self.fs)
            
    def delete_shaders(self):
        """Delete the vertex and fragment shaders."""
        if gl.glIsProgram(self.program):
            gl.glDeleteShader(self.vs)
            gl.glDeleteShader(self.fs)

    def delete_program(self):
        """Delete the shader program."""
        if gl.glIsProgram(self.program):
            gl.glDeleteProgram(self.program)
        
    def cleanup(self):
        """Clean up all shaders."""
        self.detach_shaders()
        self.delete_shaders()
        self.delete_program()
        
        
# Slicing classes
# ---------------
MAX_VBO_SIZE = 65000

class Slicer(object):
    """Handle attribute slicing, necessary because of the size
    of buffer objects which is limited on some GPUs."""
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
    def _slice_bounds(bounds, position, slice_size, regular=False):
        """Slice data bounds in a *single* slice according to the VBOs slicing.
        
        Arguments:
          * bounds: the bounds as specified by the user in `create_dataset`.
          * position: the position of the current slice.
          * slice_size: the size of the current slice.
        
        Returns:
          * bounds_sliced: the bounds for the current slice. It is a list an
            1D array of integer indices.
        
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
            
            if not regular:
                # get the bounds that fall within the sliced VBO
                ind = (bounds_sliced>=position) & (bounds_sliced<position + slice_size)
                bounds_sliced = bounds_sliced[ind]
            # HACK: more efficient algorithm when the bounds are regularly
            # spaced
            else:
                d = float(regular)
                p = position
                b0 = bounds_sliced[0]
                b1 = bounds_sliced[-1]
                s = slice_size
                i0 = max(0, int(np.ceil((p-b0)/d)))
                i1 = max(0, int(np.floor((p+s-b0)/d)))
                bounds_sliced = bounds_sliced[i0:i1+1].copy()
                ind = ((b0 >= p) and (b0 < p+s), (b1 >= p) and (b1 < p+s))
                """
                bounds_sliced = [b0 + d*i]
                (p-b0)/d <= i0 < (p+s-b0)/d
                i0 = ceil((p-b0)/d), i1 = floor((p+s-b0)/d)
                ind = (bs[0] >= p & < p+s, bs[-1])
                """
            
            # remove the onset (first index of the sliced VBO)
            bounds_sliced -= position
            # handle the case when the slice cuts between two bounds
            if not ind[0]:
                bounds_sliced = np.hstack((0, bounds_sliced))
            if not ind[-1]:
                bounds_sliced = np.hstack((bounds_sliced, slice_size))
        return enforce_dtype(bounds_sliced, np.int32)
        
    def set_size(self, size, doslice=True):
        """Update the total size of the buffer, and update
        the slice information accordingly."""
        # deactivate slicing by using a maxsize number larger than the
        # actual size
        if not doslice:
            maxsize = 2 * size
        else:
            maxsize = None
        self.size = size
        # if not hasattr(self, 'bounds'):
            # self.bounds = np.array([0, size], dtype=np.int32)
        # compute the data slicing with respect to bounds (specified in the
        # template) and to the maximum size of a VBO.
        self.slices = self._get_slices(self.size, maxsize)
        # print self.size, maxsize
        # print self.slices
        self.slice_count = len(self.slices)
    
    def set_bounds(self, bounds=None):
        """Update the bound size, and update the slice information
        accordingly."""
        if bounds is None:
            bounds = np.array([0, self.size], dtype=np.int32)
        self.bounds = bounds
        
        # is regular?
        d = np.diff(bounds)
        r = False
        if len(d) > 0:
            dm, dM = d.min(), d.max()
            if dm == dM:
                r = dm
                # log_info("Regular bounds")
        
        self.subdata_bounds = [self._slice_bounds(self.bounds, pos, size, r) \
            for pos, size in self.slices]
       
       
class SlicedAttribute(object):
    """Encapsulate methods for slicing an attribute and handling several
    buffer objects for a single attribute."""
    def __init__(self, slicer, location, buffers=None):
        self.slicer = slicer
        self.location = location
        if buffers is None:
            # create the sliced buffers
            self.create()
        else:
            log_debug("Creating sliced attribute with existing buffers " +
                str(buffers))
            # or use existing buffers
            self.load_buffers(buffers)
        
    def create(self):
        """Create the sliced buffers."""
        self.buffers = [Attribute.create() for _ in self.slicer.slices]
    
    def load_buffers(self, buffers):
        """Load existing buffers instead of creating new ones."""
        self.buffers = buffers
    
    def delete_buffers(self):
        """Delete all sub-buffers."""
        # for buffer in self.buffers:
        Attribute.delete(*self.buffers)
    
    def load(self, data):
        """Load data on all sliced buffers."""
        for buffer, (pos, size) in zip(self.buffers, self.slicer.slices):
            # WARNING: putting self.location instead of None ==> SEGFAULT on Linux with Nvidia drivers
            Attribute.bind(buffer, None)
            Attribute.load(data[pos:pos + size,...])

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
            subdata = data[pos:pos + size,...]
            submask = mask[pos:pos + size]
            # if there is at least one True in the slice mask (submask)
            if submask.any():
                # this sub-buffer contains updated indices
                subonset = submask.argmax()
                suboffset = len(submask) - 1 - submask[::-1].argmax()
                Attribute.bind(buffer, self.location)
                Attribute.update(subdata[subonset:suboffset + 1,...], subonset)

    
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
    
    def __init__(self, renderer, visual):
        """Initialize the visual renderer, create the slicer, initialize
        all variables and the shaders."""
        # register the master renderer (to access to other visual renderers)
        # and register the scene dictionary
        self.renderer = renderer
        self.scene = renderer.scene
        # register the visual dictionary
        self.visual = visual
        self.framebuffer = visual.get('framebuffer', None)
        # self.beforeclear = visual.get('beforeclear', None)
        # options
        self.options = visual.get('options', {})
        # hold all data changes until the next rendering pass happens
        self.data_updating = {}
        self.textures_to_copy = []
        # set the primitive type from its name
        self.set_primitive_type(self.visual['primitive_type'])
        # indexed mode? set in initialize_variables
        self.use_index = None
        # whether to use slicing? always True except when indexing should not
        # be used, but slicing neither
        self.use_slice = True
        # self.previous_size = None
        # set the slicer
        self.slicer = Slicer()
        # used when slicing needs to be deactivated (like for indexed arrays)
        self.noslicer = Slicer()
        # get size and bounds
        size = self.visual['size']
        bounds = np.array(self.visual.get('bounds', [0, size]), np.int32)
        # self.update_size(size, bounds)
        self.slicer.set_size(size)
        self.slicer.set_bounds(bounds)
        self.noslicer.set_size(size, doslice=False)
        self.noslicer.set_bounds(bounds)
        # compile and link the shaders
        self.shader_manager = ShaderManager(self.visual['vertex_shader'],
                                            self.visual['fragment_shader'])
                                            
        # DEBUG
        # log_info(self.shader_manager.vertex_shader)
        # log_info(self.shader_manager.fragment_shader)
                                            
        # initialize all variables
        # self.initialize_normalizers()
        self.initialize_variables()
        self.initialize_fbocopy()
        self.load_variables()
        
    def set_primitive_type(self, primtype):
        """Set the primitive type from its name (without the GL_ prefix)."""
        self.primitive_type = getattr(gl, "GL_%s" % primtype.upper())
    
    def getarg(self, name):
        """Get a visual parameter."""
        return self.visual.get(name, None)
    
    
    # Variable methods
    # ----------------
    def get_visuals(self):
        """Return all visuals defined in the scene."""
        return self.scene['visuals']
        
    def get_visual(self, name):
        """Return a visual dictionary from its name."""
        visuals = [v for v in self.get_visuals() if v.get('name', '') == name]
        if not visuals:
            return None
        return visuals[0]
        
    def get_variables(self, shader_type=None):
        """Return all variables defined in the visual."""
        if not shader_type:
            return self.visual.get('variables', [])
        else:
            return [var for var in self.get_variables() \
                            if var['shader_type'] == shader_type]
        
    def get_variable(self, name, visual=None):
        """Return a variable by its name, and for any given visual which 
        is specified by its name."""
        # get the variables list
        if visual is None:
            variables = self.get_variables()
        else:
            variables = self.get_visual(visual)['variables']
        variables = [v for v in variables if v.get('name', '') == name]
        if not variables:
            return None
        return variables[0]
        
    def resolve_reference(self, refvar):
        """Resolve a reference variable: return its true value (a Numpy array).
        """
        return self.get_variable(refvar.variable, visual=refvar.visual)
        
        
    # Initialization methods
    # ----------------------
    def initialize_fbocopy(self):
        """Create a FBO used when copying textures."""
        self.fbocopy = FrameBuffer.create()
    
    def initialize_variables(self):
        """Initialize all variables, after the shaders have compiled."""
        # find out whether indexing is used or not, because in this case
        # the slicing needs to be deactivated
        if self.get_variables('index'):
            # deactivate slicing
            self.slicer = self.noslicer
            log_debug("deactivating slicing because there's an indexed buffer")
            self.use_index = True
        else:
            self.use_index = False
        # initialize all variables
        for var in self.get_variables():
            shader_type = var['shader_type']
            # skip varying
            if shader_type == 'varying':
                continue
            name = var['name']
            # call initialize_***(name) to initialize that variable
            getattr(self, 'initialize_%s' % shader_type)(name)
        # special case for uniforms: need to load them the first time
        uniforms = self.get_variables('uniform')
        self.set_data(**dict([(v['name'], v.get('data', None)) for v in uniforms]))
    
    def initialize_attribute(self, name):
        """Initialize an attribute: get the shader location, create the
        sliced buffers, and load the data."""
        # retrieve the location of that attribute in the shader
        location = self.shader_manager.get_attribute_location(name)
        variable = self.get_variable(name)
        variable['location'] = location
        # deal with reference attributes: share the same buffers between 
        # several different visuals
        if isinstance(variable.get('data', None), RefVar):
            
            # HACK: if the targeted attribute is indexed, we should
            # deactivate slicing here
            if self.renderer.visual_renderers[variable['data'].visual].use_index:
                log_debug("deactivating slicing")
                self.slicer = self.noslicer
            
            # use the existing buffers from the target variable
            target = self.resolve_reference(variable['data'])
            variable['sliced_attribute'] = SlicedAttribute(self.slicer, location,
                buffers=target['sliced_attribute'].buffers)
        else:
            # initialize the sliced buffers
            variable['sliced_attribute'] = SlicedAttribute(self.slicer, location)
        
    def initialize_index(self, name):
        variable = self.get_variable(name)
        variable['buffer'] = Attribute.create()
        
    def initialize_texture(self, name):
        variable = self.get_variable(name)
        # handle reference variable to texture
        if isinstance(variable.get('data', None), RefVar):
            target = self.resolve_reference(variable['data'])
            variable['buffer'] = target['buffer']
            variable['location'] = target['location']
        else:
            variable['buffer'] = Texture.create(variable['ndim'],
                mipmap=variable.get('mipmap', None),
                minfilter=variable.get('minfilter', None),
                magfilter=variable.get('magfilter', None),
                )
            # NEW
            # get the location of the sampler uniform
            location = self.shader_manager.get_uniform_location(name)
            variable['location'] = location
    
    def initialize_framebuffer(self, name):
        variable = self.get_variable(name)
        variable['buffer'] = FrameBuffer.create()
        
        # bind the frame buffer
        FrameBuffer.bind(variable['buffer'])
        
        # variable['texture'] is a list of texture names in the current visual
        if isinstance(variable['texture'], basestring):
            variable['texture'] = [variable['texture']]
            
        # draw as many buffers as there are textures in that frame buffer
        FrameBuffer.draw_buffers(len(variable['texture']))
            
        for i, texname in enumerate(variable['texture']):
            # get the texture variable: 
            texture = self.get_variable(texname)
            # link the texture to the frame buffer
            FrameBuffer.bind_texture(texture['buffer'], i)
        
        # unbind the frame buffer
        FrameBuffer.unbind()
        
    def initialize_uniform(self, name):
        """Initialize an uniform: get the location after the shaders have
        been compiled."""
        location = self.shader_manager.get_uniform_location(name)
        variable = self.get_variable(name)
        variable['location'] = location
    
    def initialize_compound(self, name):
        pass
        
        
    # Normalization methods
    # ---------------------
    # def initialize_normalizers(self):
        # self.normalizers = {}
        
        
    # Loading methods
    # ---------------
    def load_variables(self):
        """Load data for all variables at initialization."""
        for var in self.get_variables():
            shader_type = var['shader_type']
            # skip uniforms
            if shader_type == 'uniform' or shader_type == 'varying' or shader_type == 'framebuffer':
                continue
            # call load_***(name) to load that variable
            getattr(self, 'load_%s' % shader_type)(var['name'])
        
    def load_attribute(self, name, data=None):
        """Load data for an attribute variable."""
        variable = self.get_variable(name)
        if variable['sliced_attribute'].location < 0:
            log_debug(("Variable '%s' could not be loaded, probably because "
                      "it is not used in the shaders") % name)
            return
        olddata = variable.get('data', None)
        if isinstance(olddata, RefVar):
            log_debug("Skipping loading data for attribute '%s' since it "
                "references a target variable." % name)
            return
        if data is None:
            data = olddata
        if data is not None:
            # normalization
            # if name in self.options.get('normalizers', {}):
                # viewbox = self.options['normalizers'][name]
                # if viewbox:
                    # self.normalizers[name] = DataNormalizer(data)
                    # # normalize data with the specified viewbox, None by default
                    # # meaning that the natural bounds of the data are used.
                    # data = self.normalizers[name].normalize(viewbox)
            variable['sliced_attribute'].load(data)
        
    def load_index(self, name, data=None):
        """Load data for an index variable."""
        variable = self.get_variable(name)
        if data is None:
            data = variable.get('data', None)
        if data is not None:
            self.indexsize = len(data)
            Attribute.bind(variable['buffer'], index=True)
            Attribute.load(data, index=True)
        
    def load_texture(self, name, data=None):
        """Load data for a texture variable."""
        variable = self.get_variable(name)
        
        if variable['buffer'] < 0:
            log_debug(("Variable '%s' could not be loaded, probably because "
                      "it is not used in the shaders") % name)
            return
        
        if data is None:
            data = variable.get('data', None)
            
        # NEW: update sampler location
        self.update_samplers = True
        
        if isinstance(data, RefVar):
            log_debug("Skipping loading data for texture '%s' since it "
                "references a target variable." % name)
            return
            
        if data is not None:
            Texture.bind(variable['buffer'], variable['ndim'])
            Texture.load(data)
            
    def load_uniform(self, name, data=None):
        """Load data for an uniform variable."""
        variable = self.get_variable(name)
        location = variable['location']
        
        if location < 0:
            log_debug(("Variable '%s' could not be loaded, probably because "
                      "it is not used in the shaders") % name)
            return
        
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
            
    def load_compound(self, name, data=None):
        pass
            
            
    # Updating methods
    # ----------------
    def update_variable(self, name, data, **kwargs):
        """Update data of a variable."""
        variable = self.get_variable(name)
        if variable is None:
            log_debug("Variable '%s' was not found, unable to update it." % name)
        else:
            shader_type = variable['shader_type']
            # skip compound, which is handled in set_data
            if shader_type == 'compound' or shader_type == 'varying' or shader_type == 'framebuffer':
                pass
            else:
                getattr(self, 'update_%s' % shader_type)(name, data, **kwargs)
    
    def update_attribute(self, name, data):#, bounds=None):
        """Update data for an attribute variable."""
        variable = self.get_variable(name)
        
        if variable['sliced_attribute'].location < 0:
            log_debug(("Variable '%s' could not be updated, probably because "
                      "it is not used in the shaders") % name)
            return
        
        # handle reference variable
        olddata = variable.get('data', None)
        if isinstance(olddata, RefVar):
            raise ValueError("Unable to load data for a reference " +
                "attribute. Use the target variable directly.""")
        variable['data'] = data
        att = variable['sliced_attribute']
        
        if olddata is None:
            oldshape = 0
        else:
            oldshape = olddata.shape
        
        # print name, oldshape, data.shape
        
        # handle size changing
        if data.shape[0] != oldshape[0]:
            log_debug(("Creating new buffers for variable %s, old size=%s,"
                "new size=%d") % (name, oldshape[0], data.shape[0]))
            # update the size only when not using index arrays
            if self.use_index:
                newsize = self.slicer.size
            else:
                newsize = data.shape[0]
            # update the slicer size and bounds
            self.slicer.set_size(newsize, doslice=not(self.use_index))
            
            # HACK: update the bounds only if there are no bounds basically
            # (ie. 2 bounds only), otherwise we assume the bounds have been
            # changed explicitely
            if len(self.slicer.bounds) == 2:
                self.slicer.set_bounds()
                
            # delete old buffers
            att.delete_buffers()
            # create new buffers
            att.create()
            # load data
            att.load(data)
            # forget previous size
            # self.previous_size = None            
        else:
            # update data
            att.update(data)
        
    def update_index(self, name, data):
        """Update data for a index variable."""
        variable = self.get_variable(name)
        prevsize = len(variable['data'])
        variable['data'] = data
        newsize = len(data)
        # handle size changing
        if newsize != prevsize:
            # update the total size (in slicer)
            # self.slicer.set_size(newsize, doslice=False)
            self.indexsize = newsize
            # delete old buffers
            Attribute.delete(variable['buffer'])
            # create new buffer
            variable['buffer'] = Attribute.create()
            # load data
            Attribute.bind(variable['buffer'], variable['ndim'], index=True)
            Attribute.load(data, index=True)
        else:
            # update data
            Attribute.bind(variable['buffer'], variable['ndim'], index=True)
            Attribute.update(data, index=True)
        
    def update_texture(self, name, data):
        """Update data for a texture variable."""
        variable = self.get_variable(name)
        
        if variable['buffer'] < 0:
            log_debug(("Variable '%s' could not be loaded, probably because "
                      "it is not used in the shaders") % name)
            return
        
        prevshape = variable['data'].shape
        variable['data'] = data
        # handle size changing
        if data.shape != prevshape:
            # delete old buffers
            # Texture.delete(variable['buffer'])
            variable['ndim'], variable['ncomponents'], _ = Texture.get_info(data)
            # create new buffer
            # variable['buffer'] = Texture.create(variable['ndim'],
                # mipmap=variable.get('mipmap', None),
                # minfilter=variable.get('minfilter', None),
                # magfilter=variable.get('magfilter', None),)
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
        
    special_keywords = ['visible',
                        'size',
                        'bounds',
                        'primitive_type',
                        'constrain_ratio',
                        'constrain_navigation',
                        ]
    def set_data(self, **kwargs):
        """Load data for the specified visual. Uploading does not happen here
        but in `update_all_variables` instead, since this needs to happen
        after shader program binding in the paint method.
        
        Arguments:
          * **kwargs: the data to update as name:value pairs. name can be
            any field of the visual, plus one of the following keywords:
              * visible: whether this visual should be visible,
              * size: the size of the visual,
              * primitive_type: the GL primitive type,
              * constrain_ratio: whether to constrain the ratio of the visual,
              * constrain_navigation: whether to constrain the navigation,
        
        """
        
        # handle compound variables
        kwargs2 = kwargs.copy()
        for name, data in kwargs2.iteritems():
            variable = self.get_variable(name)
            if variable is None:
                # log_info("variable '%s' unknown" % name)
                continue
            if variable is not None and variable['shader_type'] == 'compound':
                fun = variable['fun']
                kwargs.pop(name)
                # HACK: if the target variable in the compound is a special
                # keyword, we update it in kwargs, otherwise we update the
                # data in self.data_updating
                # print name, fun(data)
                # if name in self.special_keywords:
                    # kwargs.update(**fun(data))
                # else:
                    # self.data_updating.update(**fun(data))
                kwargs.update(**fun(data))
            # remove non-visible variables
            if not variable.get('visible', True):
                kwargs.pop(name)
        
        # handle visual visibility
        visible = kwargs.pop('visible', None)
        if visible is not None:
            self.visual['visible'] = visible
        
        # handle size keyword
        size = kwargs.pop('size', None)
        # print size
        if size is not None:
            self.slicer.set_size(size)
        
        # handle bounds keyword
        bounds = kwargs.pop('bounds', None)
        if bounds is not None:
            self.slicer.set_bounds(bounds)
            
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
        
    def copy_texture(self, tex1, tex2):
        self.textures_to_copy.append((tex1, tex2))
        
    def update_all_variables(self):
        """Upload all new data that needs to be updated."""
        # # current size, that may change following variable updating
        # if not self.previous_size:
            # self.previous_size = self.slicer.size
        # go through all data changes
        for name, data in self.data_updating.iteritems():
            if data is not None:
                # log_info("Updating variable '%s'" % name)
                self.update_variable(name, data)
            else:
                log_debug("Data for variable '%s' is None" % name)
        # reset the data updating dictionary
        self.data_updating.clear()
        
    def copy_all_textures(self):
        # copy textures
        for tex1, tex2 in self.textures_to_copy:
            # tex1 = self.get_variable(tex1)
            tex1 = self.resolve_reference(tex1)
            tex2 = self.get_variable(tex2)
            # tex2 = self.resolve_reference(tex2)
            
            # # Texture.read_buffer()
            # Texture.bind(tex2['buffer'], tex2['ndim'])
            # copy(fbo, tex_src, tex_dst, width, height)
            Texture.copy(self.fbocopy, tex1['buffer'], tex2['buffer'],
                tex1['shape'][0], tex1['shape'][1])
        self.textures_to_copy = []


    # Binding methods
    # ---------------
    def bind_attributes(self, slice=None):
        """Bind all attributes of the visual for the given slice.
        This method is used during rendering."""
        # find all visual variables with shader type 'attribute'
        attributes = self.get_variables('attribute')
        # for each attribute, bind the sub buffer corresponding to the given
        # slice
        for variable in attributes:
            loc = variable['location']
            if loc < 0:
                log_debug(("Unable to bind attribute '%s', probably because "
                "it is not used in the shaders.") % variable['name'])
                continue
            variable['sliced_attribute'].bind(slice)
            Attribute.set_attribute(loc, variable['ndim'])
            
    def bind_indices(self):
        indices = self.get_variables('index')
        for variable in indices:
            Attribute.bind(variable['buffer'], index=True)
            
    def bind_textures(self):
        """Bind all textures of the visual.
        This method is used during rendering."""
        
        textures = self.get_variables('texture')
        for i, variable in enumerate(textures):
            buffer = variable.get('buffer', None)
            if buffer is not None:
                
                # HACK: we update the sampler values here
                if self.update_samplers and not isinstance(variable['data'], RefVar):
                    Uniform.load_scalar(variable['location'], i)
                
                # NEW
                gl.glActiveTexture(getattr(gl, 'GL_TEXTURE%d' % i))
                
                Texture.bind(buffer, variable['ndim'])
            else:
                log_debug("Texture '%s' was not properly initialized." % \
                         variable['name'])
        # deactivate all textures if there are not textures
        if not textures:
            Texture.bind(0, 1)
            Texture.bind(0, 2)
        
        # no need to update the samplers after the first execution of this 
        # method
        self.update_samplers = False

    
    # Paint methods
    # -------------
    def paint(self):
        """Paint the visual slice by slice."""
        # do not display non-visible visuals
        if not self.visual.get('visible', True):
            return
            
        # activate the shaders
        try:
            self.shader_manager.activate_shaders()
        # if the shaders could not be successfully activated, stop the
        # rendering immediately
        except Exception as e:
            log_info("Error while activating the shaders: " + str(e))
            return
            
        # update all variables
        self.update_all_variables()
        # bind all texturex for that slice
        self.bind_textures()
        # paint using indices
        if self.use_index:
            self.bind_attributes()
            self.bind_indices()
            Painter.draw_indexed_arrays(self.primitive_type, self.indexsize)
        # or paint without
        elif self.use_slice:
            # draw all sliced buffers
            for slice in xrange(len(self.slicer.slices)):
                # get slice bounds
                slice_bounds = self.slicer.subdata_bounds[slice]
                # print slice, slice_bounds
                # bind all attributes for that slice
                self.bind_attributes(slice)
                # call the appropriate OpenGL rendering command
                # if len(self.slicer.bounds) <= 2:
                # print "slice bounds", slice_bounds
                if len(slice_bounds) <= 2:
                    Painter.draw_arrays(self.primitive_type, slice_bounds[0], 
                        slice_bounds[1] -  slice_bounds[0])
                else:
                    Painter.draw_multi_arrays(self.primitive_type, slice_bounds)
        
        self.copy_all_textures()
        
        # deactivate the shaders
        self.shader_manager.deactivate_shaders()


    # Cleanup methods
    # ---------------
    def cleanup_attribute(self, name):
        """Cleanup a sliced attribute (all sub-buffers)."""
        variable = self.get_variable(name)
        variable['sliced_attribute'].delete_buffers()
    
    def cleanup_texture(self, name):
        """Cleanup a texture."""
        variable = self.get_variable(name)
        Texture.delete(variable['buffer'])
        
    def cleanup(self):
        """Clean up all variables."""
        log_debug("Cleaning up all variables.")
        for variable in self.get_variables():
            shader_type = variable['shader_type']
            if shader_type in ('attribute', 'texture'):
                getattr(self, 'cleanup_%s' % shader_type)(variable['name'])
        # clean up shaders
        self.shader_manager.cleanup()
        
        
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
        """Initialize the renderer using the information on the scene.
        
        Arguments:
          * scene: a Scene dictionary with a `visuals` field containing
            the list of visuals.
        
        """
        self.scene = scene
        self.viewport = (1., 1.)
        self.visual_renderers = {}
    
    def set_renderer_options(self):
        """Set the OpenGL options."""
        options = self.scene.get('renderer_options', {})
        
        # use vertex buffer object
        gl.glEnableClientState(gl.GL_VERTEX_ARRAY)

        # used for multisampling (antialiasing)
        if options.get('antialiasing', None):
            gl.glEnable(gl.GL_MULTISAMPLE)
            
        # used for sprites
        if options.get('sprites', True):
            gl.glEnable(gl.GL_VERTEX_PROGRAM_POINT_SIZE)
            gl.glEnable(gl.GL_POINT_SPRITE)
        
        # enable transparency
        if options.get('transparency', True):
            gl.glEnable(gl.GL_BLEND)
            blendfunc = options.get('transparency_blendfunc',
                ('SRC_ALPHA', 'ONE_MINUS_SRC_ALPHA')
                # ('ONE_MINUS_DST_ALPHA', 'ONE')
                )
            blendfunc = [getattr(gl, 'GL_' + x) for x in blendfunc]
            gl.glBlendFunc(*blendfunc)
            
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
        
    def get_renderer_option(self, name):
        return self.scene.get('renderer_options', {}).get(name, None)
        
        
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
    def set_data(self, name, **kwargs):
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
        # call set_data on the given visual renderer
        if name in self.visual_renderers:
            self.visual_renderers[name].set_data(**kwargs)
        
    def copy_texture(self, name, tex1, tex2):
        self.visual_renderers[name].copy_texture(tex1, tex2)
    
        
    # Rendering methods
    # -----------------
    def initialize(self):
        """Initialize the renderer."""
        # print the renderer information
        for key, value in GLVersion.get_renderer_info().iteritems():
            if key is not None and value is not None:
                log_debug(key + ": " + value)
        # initialize the renderer options using the options set in the Scene
        self.set_renderer_options()
        # create the VisualRenderer objects
        self.visual_renderers = OrderedDict()
        for visual in self.get_visuals():
            name = visual['name']
            self.visual_renderers[name] = GLVisualRenderer(self, visual)
            
        # detect FBO
        self.fbos = []
        for name, vr in self.visual_renderers.iteritems():
            fbos = vr.get_variables('framebuffer')
            if fbos:
                self.fbos.extend([fbo['buffer'] for fbo in fbos])
            
    def clear(self):
        """Clear the scene."""
        # clear the buffer (and depth buffer is 3D is activated)
        if self.scene.get('renderer_options', {}).get('activate3D', None):
            gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        else:
            gl.glClear(gl.GL_COLOR_BUFFER_BIT)
        
    def paint(self):
        """Paint the scene."""
        
        # non-FBO rendering
        if not self.fbos:
            self.clear()
            for name, visual_renderer in self.visual_renderers.iteritems():
                visual_renderer.paint()
        
        
        # render each FBO separately, then non-VBO
        else:
            for fbo in self.fbos:
                FrameBuffer.bind(fbo)
                
                # fbo index
                ifbo = self.fbos.index(fbo)
                
                # clear
                self.clear()
                
                # paint all visual renderers
                for name, visual_renderer in self.visual_renderers.iteritems():
                    if visual_renderer.framebuffer == ifbo:
                        # print ifbo, visual_renderer
                        visual_renderer.paint()
    
            # finally, paint screen
            FrameBuffer.unbind()
    
            # render screen (non-FBO) visuals
            self.clear()
            for name, visual_renderer in self.visual_renderers.iteritems():
                if visual_renderer.framebuffer == 'screen':
                    # print "screen", visual_renderer
                    visual_renderer.paint()
        
            # print
        
    def resize(self, width, height):
        """Resize the canvas and make appropriate changes to the scene."""
        # paint within the whole window
        gl.glViewport(0, 0, width, height)
        # compute the constrained viewport
        x = y = 1.0
        if self.get_renderer_option('constrain_ratio'):
            if height > 0:
                aw = float(width) / height
                ar = self.get_renderer_option('constrain_ratio')
                if ar is True:
                    ar = 1.
                if ar < aw:
                    x, y = aw / ar, 1.
                else:
                    x, y = 1., ar / aw
        self.viewport = x, y
        width = float(width)
        height = float(height)
        # update the viewport and window size for all visuals
        for visual in self.get_visuals():
            self.set_data(visual['name'],
                          viewport=self.viewport,
                          window_size=(width, height))
    
    
    # Cleanup methods
    # ---------------
    def cleanup(self):
        """Clean up all allocated OpenGL objects."""
        for name, renderer in self.visual_renderers.iteritems():
            renderer.cleanup()
        
