import sys
import time
import numpy as np
import OpenGL.GL as gl
import OpenGL.arrays.vbo as glvbo
import OpenGL.GLUT as glut
from tools import enum, memoize, enforce_dtype
from default_shaders import DEFAULT_SHADERS
import ctypes
from debugtools import log_debug, log_info, log_warn

__all__ = ['PrimitiveType', 'PaintManager']

# Whether to use the array extension of PyOpenGL. Should be False.
USE_PYOPENGL_ARRAY = False

# Enumerations
# ------------
# Enumeration with the possible primitive types. They exactly correspond
# to their OpenGL counterparts.
PrimitiveType = enum("Points",
                     "Lines", "LineStrip", "LineLoop",
                     "Triangles", "TriangleStrip", "TriangleFan")

# Primitive type converter.
GL_PRIMITIVE_TYPE_CONVERTER = {
    PrimitiveType.Points: gl.GL_POINTS,
    PrimitiveType.Lines: gl.GL_LINES,
    PrimitiveType.LineStrip: gl.GL_LINE_STRIP,
    PrimitiveType.LineLoop: gl.GL_LINE_LOOP,
    PrimitiveType.Triangles: gl.GL_TRIANGLES,
    PrimitiveType.TriangleStrip: gl.GL_TRIANGLE_STRIP,
    PrimitiveType.TriangleFan: gl.GL_TRIANGLE_FAN,
}

# Converter between Numpy and OpenGL type
NP_GL_TYPE_CONVERTER = {
    np.float32:gl.GL_FLOAT,
    np.int32:gl.GL_INT,
    np.bool:gl.GL_BOOL,
}


def _get_value_type(value):
    """Give information about an uniform value type."""
    # array
    if isinstance(value, np.ndarray):
        is_float = value.dtype == np.float32
        is_bool= value.dtype == np.bool
        size, ndim = value.shape
    # tuple
    elif type(value) is tuple:
        is_float = (type(value[0]) == float) | (type(value[0]) == np.float32)
        is_bool = type(value[0]) == bool
        ndim = len(value)
        size = None
    # scalar value
    else:
        is_float = type(value) == float
        is_bool = type(value) == bool
        ndim = 1
        size = None
    return dict(is_float=is_float, is_bool=is_bool, ndim=ndim, size=size)

# global counter for the buffer attribute location, allows to avoid 
# specifying explicitely an unique location for each buffer
SHADER_ATTRIBUTE_LOCATION = 0
def get_new_attribute_location():
    global SHADER_ATTRIBUTE_LOCATION
    loc = SHADER_ATTRIBUTE_LOCATION
    SHADER_ATTRIBUTE_LOCATION += 1
    return loc
    
def reset_attribute_location():
    """Set the counter to 0 at initialization."""
    global SHADER_ATTRIBUTE_LOCATION
    SHADER_ATTRIBUTE_LOCATION = 0

    
    
# VBO functions
# -------------

# Maximum size of a VBO, generally to 65k. You might try to increase it
# in order to improve performance, but be very careful since no error will
# be raised if you cross the limit: all values defined after that limit
# will be zero, so you might just have very weird results! Make sure to test.
MAX_VBO_SIZE = 65000

def create_vbo(data):
    """Create an OpenGL Vertex Buffer Object.
    
    The VBO creation uses the PyOpenGL array extension or not, depending on 
    the value of the global variable `USE_PYOPENGL_ARRAY`.
    
    Arguments:
      * data: a 2D Numpy array to put in the VBO. It can contain more than 65k 
        points, in this case several VBOs are being created under the hood.
        This is all transparent in this class interface.
        
    Returns:
      * buffer: either a PyOpenGL VBO object, or a buffer index.
      
    """
    if USE_PYOPENGL_ARRAY:
        buffer = glvbo.VBO(data)
    else:
        buffer = gl.glGenBuffers(1)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, buffer)
        gl.glBufferData(gl.GL_ARRAY_BUFFER, data, 
                        gl.GL_DYNAMIC_DRAW)
    return buffer
    
def bind_vbo(buffer):
    """Bind a VBO.
    
    Use this function before using a VBO (like updating the data or rendering
    it).
    
    Arguments:
      * buffer: the object returned by `create_vbo`.
      
    """
    if USE_PYOPENGL_ARRAY:
        buffer.bind()
    else:
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, buffer)

def update_vbo(buffer, newdata, onset=None):
    """Update a VBO.
    
    Arguments:
      * buffer: the object returned by `create_vbo`.
      * newdata: the array with the new data, it does not need to have the exact
        same shape as the original data.
      * onset: the onset starting from which the data should be updated.
    
    """
    if onset is None:
        onset = 0
    # convert onset into bytes count
    onset *= newdata.shape[1] * newdata.itemsize
    bind_vbo(buffer)
    gl.glBufferSubData(gl.GL_ARRAY_BUFFER, onset, newdata)
        

# Texture functions
# -----------------
def create_texture(data, size, ndim, ncomponents):
    """Create an OpenGL texture.
    
    Arguments:
      * data: an NxMx3 or NxMx4 array.
      * size: the size of the texture, i.e. (N, M).
      * ndim: the number of dimensions of the texture (1 or 2).
      * ncomponents: the number of channel components (3 or 4).
    
    Returns:
      * tex: the texture identifier.
    
    """
    textype = getattr(gl, "GL_TEXTURE_%dD" % ndim)
    tex = gl.glGenTextures(1)
    gl.glBindTexture(textype, tex)
    gl.glPixelStorei(gl.GL_UNPACK_ALIGNMENT, 1)
    gl.glTexParameteri(textype, gl.GL_TEXTURE_WRAP_S, gl.GL_CLAMP)
    gl.glTexParameteri(textype, gl.GL_TEXTURE_WRAP_T, gl.GL_CLAMP)
    gl.glTexParameteri(textype, gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST)
    gl.glTexParameteri(textype, gl.GL_TEXTURE_MIN_FILTER, gl.GL_NEAREST)
    
    # ncomponents==1 ==> GL_R, 3 ==> GL_RGB, 4 ==> GL_RGBA
    component_type = getattr(gl, ["GL_INTENSITY8", None, "GL_RGB", "GL_RGBA"] \
                                        [ncomponents - 1])
    
    # set texture data
    if ndim == 1:
        gl.glTexImage1D(textype, 0, component_type, size, 0, component_type,
                        gl.GL_UNSIGNED_BYTE, data)
    elif ndim == 2:
        gl.glTexImage2D(textype, 0, component_type, size[0], size[1], 0,
                        component_type, gl.GL_UNSIGNED_BYTE, data)

    return tex

def update_texture(tex, newdata, size, ndim, ncomponents):
    """Update an OpenGL texture.
    
    Arguments:
      * tex: the texture identifier returned by `create_texture`.
      * newdata: an NxMx3 or NxMx4 array.
      * size: the size of the texture, i.e. (N, M).
      * ndim: the number of dimensions of the texture (1 or 2).
      * ncomponents: the number of channel components (3 or 4).
    
    """
    textype = getattr(gl, "GL_TEXTURE_%dD" % ndim)
    gl.glBindTexture(textype, tex)
    
    # ncomponents==1 ==> GL_R, 3 ==> GL_RGB, 4 ==> GL_RGBA
    component_type = getattr(gl, ["GL_R", None, "GL_RGB", "GL_RGBA"] \
                                        [ncomponents - 1])
    
    # update texture data
    if ndim == 1:
        gl.glTexSubImage1D(textype, 0, 0, size,
                            component_type, gl.GL_UNSIGNED_BYTE, newdata)
    elif ndim == 2:
        gl.glTexSubImage2D(textype, 0, 0, 0, size[0], size[1],
                            component_type, gl.GL_UNSIGNED_BYTE, newdata)

    
    
# PaintManager class
# ------------------                   
class PaintManager(object):
    """Defines what to render in the widget."""
    
    # Background color.
    bgcolor = (0, 0, 0, 0)
    
    def __init__(self):
        # current absolute translation offset, used because glTranslate is
        # relative to the current position
        self.current_offset = (0, 0)
        
        # list of datasets
        self.datasets = []

        # list of text strings to display
        # self.texts = []
        self.permanent_overlays = []
        self.transient_overlays = []
        
    # Internal methods
    # ----------------
    def _get_slices(self, size):
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
    
    def _slice_data(self, data, slices=None):
        """Slice an array according to the dataset slices.
        
        Arguments:
          * data: a Nx2 array.
          * slices: the slices returned by `_get_slices`, or `None` (in which
            case they will be computed).
          
        Returns:
          * data_sliced: a list of triplets `(subdata, position, slice_size)`.
          
        """
        if slices is None:
            slices = self._get_slices(data.shape[0])
        return [(data[position:position+size,:], position, size) for position, size in slices]
    
    def _slice_bounds(self, bounds, position, slice_size):
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
        
    def _set_drawing_size(self, primitive_type, size):
        """Set the drawing size.
        
        Arguments:
          * primitive_type: a PrimitiveType enum value.
          * size: the size of the point or line (1 by default).
          
        """
        if primitive_type == PrimitiveType.Points:
            gl.glPointSize(size)
        elif primitive_type == PrimitiveType.LineStrip:
            gl.glLineWidth(size)
        
    def _set_color(self, color):
        """Set the current paint color.
        
        Arguments:
          * color: a 3- or 4- tuple (RGB or RGBA).
        
        """
        gl.glColor(*color)
        
    def _set_vbo(self, vbo, location, ndim, dtype=None, gltype=None):
        """Activate the VBO before rendering.
        
        Arguments:
          * vbo: the buffer object returned by the `create_vbo` that was used
            for the VBO creation.
          * location: the shader attribute location (int).
          * ndim: the size of each vertex in the current buffer (number of 
            columns in the data array).
          * dtype=None: the Numpy dtype of the corresponding data, used to 
            specify the corresponding OpenGL type.
          * gltype=None: the OpenGL type, if `None`, it is deduced from the dtype.
            
        """
        if gltype is None:
            if dtype is None:
                dtype = np.float32
            gltype = NP_GL_TYPE_CONVERTER[dtype]
        bind_vbo(vbo)
        gl.glEnableVertexAttribArray(location)
        gl.glVertexAttribPointer(location, ndim, gltype, gl.GL_FALSE, 0, None)
        
    # Data creation methods
    # ---------------------
    def create_dataset(self, size, bounds=None,
                       primitive_type=None, color=None,
                       vertex_shader=None,
                       fragment_shader=None,
                       is_static=False,
                       **uniforms):
        """Create a dataset.
        
        A dataset is the combination of:
          * a set of `N` points,
          * a vertex shader and fragment shader source codes,
          * any number of buffers, each buffer having a name and corresponding 
            to an actual data array,
          * a set of textures (TODO: only one texture support is implemented 
            currently).
        
        All the buffers are processed on the GPU through vertex and fragment
        shaders. The role of shaders is to transform data contained in these
        buffers into 2D or 3D colored vertices on the screen.
        The vertex shader generates the positions of the vertices.
        The fragment shader generates the colors of the vertices.
        
        Default shaders are provided in the helper painting methods.
        Custom shaders can be specified if needed. That's an advanced 
        and extremely powerful feature. One needs to know the OpenGL 
        programmable pipeline and the GLSL language in order to write their
        own shaders.
        
        Arguments:
          * size: the size of the dataset, i.e. the number of points.
          * bounds=None: the data bounds separating the individual objects to
            display. It should be an array of int32 with all bound indices.
            The first index must be 0, the last one is `size`. Every index
            gives the position of the first point in the current primitive.
            The default (`None`) is just `[0, size]`.
          * primitive_type=None: a member of the `PrimitiveType` enumeration
            with the primitive type to render for this dataset. By default,
            it is `PrimitiveType.Points`.
          * color=None: the default color of the rendered primitives. It is
            yellow by default. This value may not be used depending on the
            specific fragment shader.
          * vertex_shader=None: the source code of the vertex shader.
          * fragment_shader=None: the source code of the fragment shader.
          * is_static=False: whether the rendered objects should be transformed
            by the interactive navigation or stay at a fixed position in the
            window.
          * **uniforms: keyword arguments of uniform variables, with their 
            initial values.
          
        Returns:
          * dataset: a dictionary containing all the information about
            the dataset, and that can be used in the methods of `PaintManager`.
        
        """
        if bounds is None:
            bounds = np.array([0, size], np.int32)

        # reset the attribute location
        reset_attribute_location()
            
        dataset = {}
        dataset["size"] = size
        dataset["bounds"] = enforce_dtype(bounds, np.int32)
        dataset["slices_count"] = int(np.ceil(size / float(MAX_VBO_SIZE)))
        dataset["vertex_shader"] = vertex_shader
        dataset["fragment_shader"] = fragment_shader
        dataset["color"] = color
        # dataset["primitive_size"] = primitive_size
        dataset["primitive_type"] = primitive_type
        dataset["buffers"] = {}
        dataset["textures"] = {}
        
        # compute slices according to the maximum size of a VBO
        slices = self._get_slices(size)
        dataset["slices"] = slices
        
        # subdata_bounds is the bounds (as a list) for the current subdata
        dataset["subdata_bounds"] = [self._slice_bounds(bounds, pos, size) for pos, size in slices]
        
        # save uniforms with their names, values, and type (and dtype if 
        # they are Numpy arrays)
        dataset["uniforms"] = {}
        for name, value in uniforms.iteritems():
            uniform = dict(
                value=value,
                type=type(value),
                invalidated=True,
            )
            if isinstance(value, np.ndarray):
                # enforce 32 bits for floats and integers
                # if value.dtype == np.float64:
                    # value = enforce_dtype(value, np.float32)
                # if value.dtype == np.int64:
                    # value = enforce_dtype(value, np.int32)
                uniform = self.validate_uniform_value(uniform)
                uniform["dtype"] = value.dtype
            dataset["uniforms"][name] = uniform
        
        self.datasets.append(dataset)
        return dataset
        
    def add_buffer(self, name, data, dataset=None,
                   attribute_location=None):
        """Add a data buffer to a dataset.
        
        A buffer is linked to a dataset and is defined by:
          * an unique name, used in the vertex shader,
          * a data array, of size N x ndim where N is the dataset size,
          * an unique location (a positive integer) also used in the vertex
            shader.
            
        There is a line like the following one at the beginning of the vertex 
        shader source code:

            layout(location = 0) in vec4 position;
        
        This line links a buffer name with its location, and specifies the type
        of every vertex in this buffer (here, 4 float32 values for 3D + 1D 
        homogeneous coordinates). There is one such line for every buffer
        that has to be used in a given dataset. Shader variable declarations
        can also be automatically written with `%AUTODECLARATIONS%` at the
        beginning of the vertex shader. It will be automatically replaced
        by the corresponding declarations based on the added buffers.
        
        Arguments:
          * name: the name of this buffer, to be used in the vertex shader
            source code.
          * data: a Numpy array with the data attached to this buffer. Its size
            should be `size x ndim` where `size` is the dataset size.
          * dataset=None: the dataset containing the buffer to be created. It
            is theobject returned by `create_dataset`. By default, the first
            dataset that has been defined.
          * attribute_location: the location of this buffer, calculated
            automatically if it is not specified. It should be unique.
            You should not need to change it.
        
        Returns:
          * buffer: a dictionary containing all the information related to
            this buffer, and to be used in the methods of `PaintManager`.
        
        """
        if dataset is None:
            dataset = self.datasets[0]
        
        # enforce 32 bits for arrays of floats
        if data.dtype == np.float64:
            data = enforce_dtype(data, np.float32)
        
        # enforce 2 dimensions for the array
        if data.ndim == 1:
            data = data.reshape((-1, 1))
        
        # default parameters
        ndim = data.shape[1]
        if data.shape[0] != dataset["size"]:
            raise ValueError("The shape of 'data' should be \
                              dataset[size] x ndim")
        if attribute_location is None:
            attribute_location = get_new_attribute_location()
        
        # create the buffer info
        buffer = {}
        buffer["name"] = name
        buffer["data"] = data
        buffer["dtype"] = data.dtype
        buffer["ndim"] = ndim
        buffer["size"] = dataset["size"]
        buffer["bounds"] = dataset["bounds"]
        buffer["slices"] = dataset["slices"]
        buffer["subdata_bounds"] = dataset["subdata_bounds"]
        buffer["attribute_location"] = attribute_location
        
        # slice data
        data_sliced = self._slice_data(data, dataset["slices"])
        buffer["vbos"] = [(create_vbo(subdata), pos, size) for subdata, pos, size in data_sliced]
        
        # save this buffer info into the dataset
        dataset["buffers"][name] = buffer
        
        return buffer
        
    def add_texture(self, name, data, dataset=None,
                   attribute_location=None):
        """Add a texture to a dataset.
        
        Arguments:
          * name: the name of the texture.
          * data: a 3D array with the texture.
          * dataset=None: the dataset containing the buffer to be created. It
            is the object returned by `create_dataset`. By default, the first
            dataset that has been defined.
        
        """
        if dataset is None:
            dataset = self.datasets[0]
                   
        # convert from float in [0,1] to uint8
        if (data.dtype == np.float32) or (data.dtype == np.float64):
            data = np.array(255*data, dtype=np.uint8)
                   
        # enforce 2 dimensions for the array
        if data.ndim == 1:
            data = data.reshape((-1, 1))
        
        # enforce 3D
        # if data.ndim == 2:
            # data = np.tile(data.reshape(data.shape+(1,)), (1, 1, 3))
        
        # default parameters
        ndim = data.ndim
        if attribute_location is None:
            # TODO: allow several textures
            attribute_location = 0
        
        # compute the number of dimensions and color components
        if ndim == 1:
            ncomponents = 1
            size = data.shape[0]
        elif ndim == 2:
            # 2 dimensions ==> only 1 component
            ncomponents = 1
            size = data.shape
        elif ndim == 3:
            # along third dimension: color components
            ncomponents = data.shape[2]
            # 2D texture
            ndim = 2
            size = data.shape[:2]
            
        # create the texture info
        texture = {}
        texture["name"] = name
        texture["data"] = data
        texture["dtype"] = data.dtype
        texture["ndim"] = ndim
        texture["ncomponents"] = ncomponents
        texture["size"] = size
        texture["attribute_location"] = attribute_location
        
        # initialize texture
        texture["texture"] = create_texture(data, size, ndim, ncomponents)
        
        # save this texture info into the dataset
        dataset["textures"][name] = texture
        
        # add texture uniform sampler
        # TODO: check this when several textures are used. this currently works
        # for 1 texture only
        name = "tex_sampler%d" % attribute_location
        dataset["uniforms"][name] = dict(
            value=0,
            type=int,
            invalidated=True,
        )
        
        return texture
        
    # Data update methods
    # -------------------
    def update_buffer(self, buffer, newdata, dataset=None, mask=None):
        """Update a data buffer with a new data array.
        
        Arguments:
          * buffer: the buffer object returned by `add_buffer`.
          * newdata: a Numpy array with the exact same shape as the original
            data used in `add_buffer`.
          * mask: a 1D Numpy array of booleans with `size` elements. This array
            indicates which points have been updated. It is only used as a 
            performance hint, by default all points are updated. If the boolean
            value in this array corresponding to index `i` is `True`, this
            point will be updated. However, if it `False`, it may or may not
            be updated: it is not guaranted that it won't be updated.
            The reason for this is that a VBO can contain no more than 65k
            points, and several VBOs are used under the hood if the buffer size
            is greater than that. When updating a data buffer, all 
            corresponding VBOs are updated. For performance reasons, it is
            unncessary to update a VBO is no data inside has changed.
        
        """
        
        if dataset is not None and type(buffer) is str:
            buffer = dataset["buffers"][buffer]
        
        size = buffer["size"]
        ndim = buffer["ndim"]
        
        if newdata.dtype == np.float64:
            newdata = enforce_dtype(newdata, np.float32)
        
        # enforce 2 dimensions for the array
        if newdata.ndim == 1:
            newdata = newdata.reshape((-1, 1))
        
        # check newdata shape
        if newdata.shape[0] != size:
            raise ValueError("The shape of 'newdata' should be \
                              dataset[size] x ndim")
        
        # default mask
        if mask is None:
            mask = np.ones(size, dtype=bool)
            
        # slice data
        data_sliced = self._slice_data(newdata, buffer["slices"])
        
        # is the current subVBO within the given [onset, offset]?
        within = False
        # update VBOs
        for slice_index in xrange(len(data_sliced)):
            newsubdata, pos, slice_size = data_sliced[slice_index]
            vbo, _, _ = buffer["vbos"][slice_index]
            # subdata_bounds is the bounds (as a list) for the current subdata
            subdata_bounds = buffer["subdata_bounds"][slice_index]
            # mask of updated indices in the subVBO
            submask = mask[pos:pos + slice_size]
            # if there is at least one True in the slice mask (submask)
            if submask.any():
                # this subVBO contains updated indices
                subonset = submask.argmax()
                suboffset = len(submask) - 1 - submask[::-1].argmax()
                update_vbo(vbo, newsubdata[subonset:suboffset + 1], subonset)
    
    def update_texture(self, texture, newdata):
        """Update a texture.
        
        Arguments:
          * texture: the texture object returned by `create_texture`, or a 
            dataset, in which case the first texture defined in this dataset is
            used.
          * newdata: the new texture data, which needs to have the exact same
            size as the original texture data.
          
        """
        # convert from float in [0,1] to uint8
        if newdata.dtype == np.float32:
            newdata = np.array(255*newdata, dtype=np.uint8)

        # texture may be a dataset object, in which case get the first texture
        if "texture" not in texture:
            texture = texture["textures"]["position"]
        update_texture(texture["texture"], newdata, texture["size"], 
                        texture["ndim"], texture["ncomponents"])
        
    # Helper plotting methods
    # -----------------------
    def add_plot(self, X, Y, color=None, is_static=False, primitive_type=None,
                    vertex_shader=None, fragment_shader=None):
        """Add points on the plot.
        
        Arguments:
          * X: the x coordinates as an `Npoints` 1D array, or an `Nprimitives x 
            Npoints` array. In this case, `Nprimitives` different primitives
            will be plotted in a single OpenGL command, which is the most
            efficient possible way.
          * Y: the y coordinates, of the exact same shape as `X`.
          * color=None: the color as a tuple or an array.
          * is_static=False: whether this plot is in a static position or not.
          * primitive_type=None: a member of the `PrimitiveType` enumeration.
          * vertex_shader=None: the vertex shader source code.
          * fragment_shader=None: the fragment shader source code.
          
        Returns:
          * dataset: the newly created dataset.
         
        """
        n = X.size
        # check arguments
        if X.shape != Y.shape:
            raise ValueError("")
        if color is None:
            color = (1, 1, 0)
        kwargs = {}
        # color
        if isinstance(color, np.ndarray):
            if X.ndim == 1:
                if color.shape[0] != n:
                    raise ValueError("The color size should be len(X).")
            elif X.ndim == 2:
                if color.shape[0] != X.shape[0]:
                    raise ValueError("The color size should be X.shape[1].")
        elif color is not None:
            kwargs["color"] = color
        if primitive_type is None:
            primitive_type = PrimitiveType.Points
        # fill the data array
        data = np.empty((n, 2), dtype=np.float32)
        data[:,0] = X.ravel()
        data[:,1] = Y.ravel()
        if (X.ndim > 1) and (min(X.shape) > 1):
            kwargs["bounds"] = np.arange(0, X.size + 1, X.shape[1])
            color = np.repeat(color, X.shape[1], axis=0)
        # create dataset
        ds = self.create_dataset(n, primitive_type=primitive_type,
                                 is_static=is_static, 
                                 vertex_shader=vertex_shader,
                                 fragment_shader=fragment_shader,
                                 **kwargs)
        self.add_buffer("position", data, dataset=ds)
        if isinstance(color, np.ndarray):
            self.add_buffer("color", color, dataset=ds)
        return ds
    
    def add_textured_rectangle(self, texture, points=None, is_static=False,
                                vertex_shader=None, fragment_shader=None):
        """Helper function to add a textured rectangle (image).
        
        Arguments:
          * texture: a NxMxD array with D=3 (RGB) or 4 (RGBA).
          * points=None: coordinates of the rectangle: (x0, y0, x1, y1).
            By default: [-1,1]^2.
          * is_static=False: whether this plot is in a static position or not.
          * vertex_shader=None: the vertex shader source code.
          * fragment_shader=None: the fragment shader source code.
        
        Returns:
          * dataset: the newly created dataset.
        
        """
        if vertex_shader is None:
            vertex_shader = DEFAULT_SHADERS["textured_rectangle"]["vertex"]
        if fragment_shader is None:
            fragment_shader = DEFAULT_SHADERS["textured_rectangle"]["fragment"]
        if points is None:
            points = (-1, -1, 1, 1)
        x0, y0, x1, y1 = points
        x0, x1 = min(x0, x1), max(x0, x1)
        y0, y1 = min(y0, y1), max(y0, y1)
        name = "position" #"textured_rectangle%d" % len(self.datasets)
        coordinates_name = "texture_coordinates" #%d" % len(self.datasets)
        ds = self.create_dataset(4,
                                primitive_type=PrimitiveType.TriangleStrip, 
                                is_static=is_static,
                                vertex_shader=vertex_shader,
                                fragment_shader=fragment_shader)
                                
        data = np.zeros((4,2), dtype=np.float32)
        data[0,:] = (x0, y0)
        data[1,:] = (x1, y0)
        data[2,:] = (x0, y1)
        data[3,:] = (x1, y1)
        self.add_buffer(name, data, dataset=ds)
                                
        coordinates = np.zeros((4,2), dtype=np.float32)
        coordinates[0,:] = (0, 1)
        coordinates[1,:] = (1, 1)
        coordinates[2,:] = (0, 0)
        coordinates[3,:] = (1, 0)
        self.add_buffer(coordinates_name, coordinates, dataset=ds)
        
        self.add_texture(name, texture, dataset=ds)        
        return ds

    def add_sprites(self, X, Y, texture, color=None, size=None, is_static=False):
        """Helper function to add sprites (a texture at multiple positions).
        
        Arguments:
          * X, Y: positions as Npositions-vectors.
          * texture: a NxMx3 or NxMx4 array with the texture data (RGB(A)
            channels).
          * color=None: the color of the sprites as an Npositions x 3 array.
          * size=None: the size of the sprite, by default, the size of the
            texture. The unit is the pixel.
          * is_static=None: if True, the sprites won't be transformed by the
            interactive navigation.
        
        Returns:
          * dataset: the newly created dataset.
        
        """
        gl.glEnable(gl.GL_POINT_SPRITE)
        if isinstance(color, np.ndarray):
            vertex_shader = DEFAULT_SHADERS["sprites_color"]["vertex"]
            fragment_shader = DEFAULT_SHADERS["sprites_color"]["fragment"]
        else:
            vertex_shader = DEFAULT_SHADERS["sprites"]["vertex"]
            fragment_shader = DEFAULT_SHADERS["sprites"]["fragment"]
        if size is None:
            size = max(texture.shape)
        # convert size into float because the associated uniform is a float
        size = float(size)
        kwargs = {}
        if type(color) is tuple:
            kwargs["color"] = color
        ds = self.create_dataset(len(X),
                                primitive_type=PrimitiveType.Points,
                                vertex_shader=vertex_shader,
                                fragment_shader=fragment_shader,
                                point_size=size,
                                is_static=is_static,
                                **kwargs)
        pos = np.empty((len(X), 2))
        pos[:,0] = X
        pos[:,1] = Y
        self.add_buffer("position", pos, dataset=ds)
        if isinstance(color, np.ndarray):
            self.add_buffer("color", color, dataset=ds)
        self.add_texture("texture", texture, dataset=ds)
        return ds
        
    # Buffer methods
    # --------------
    def activate_buffer(self, dataset, buffer_name, slice_index,
                        do_activate=True):
        """Activate a buffer before rendering, so that the vertices inside it
        are processed through the shaders.
        
        Arguments:
          * dataset: the dataset object, returned by `create_dataset`.
          * buffer_name: a string with the buffer name, should correspond to 
            the vertex name in the vertex shader.
          * slice_index: the index of the slice to activate. For each slice,
            all buffers need to be activated.
          * do_activate=True: activate or deactivate the buffer in this
            rendering pass. Set to False if this buffer is currently unused,
            it should be more efficient. In this case, the corresponding
            variable in the vertex shader will have all its coordinates to 0
            by default.
            
        """
        buffer = dataset["buffers"][buffer_name]
        location = buffer["attribute_location"]
        ndim = buffer["ndim"]
        vbo, pos, size = buffer["vbos"][slice_index]
        
        bind_vbo(vbo)
        if do_activate:
            gl.glEnableVertexAttribArray(location)
            gl.glVertexAttribPointer(location, ndim, gl.GL_FLOAT, gl.GL_FALSE, 0, None)
        else:
            gl.glDisableVertexAttribArray(location)
            
    # Shader methods
    # --------------
    def set_default_shaders(self, dataset):
        """Set the default shaders if no shaders are specified by the user,
        depending on which buffers were added in the dataset at initialization
        time.
        
        Arguments:
          * dataset: the dataset object.
        
        """
        vs = dataset["vertex_shader"]
        fs = dataset["fragment_shader"]
        
        # specify default shaders
        # just position
        if "color" not in dataset["buffers"]:
            if vs is None:
                dataset["vertex_shader"] = DEFAULT_SHADERS["position"]["vertex"]
            if fs is None:
                dataset["fragment_shader"] = DEFAULT_SHADERS["position"]["fragment"]
        # position and color
        elif "position" in dataset["buffers"]:
            if vs is None:
                dataset["vertex_shader"] = DEFAULT_SHADERS["position_color"]["vertex"]
            if fs is None:
                dataset["fragment_shader"] = DEFAULT_SHADERS["position_color"]["fragment"]
                
    def process_vertex_shader_source(self, dataset):
        """Process templated vertex shader source.
        
        This method replaces %AUTODECLARATIONS% with the actual shader variable
        declarations, based on what the dataset contains.
        
        Arguments:
          * dataset: the dataset.
          
        Returns:
          * dataset: the dataset with the updated shader code.
        
        """
        
        vs = dataset["vertex_shader"]
        
        # autodeclaration of buffers
        declarations = "// Buffer declarations.\n"
        for name, buffer in dataset["buffers"].iteritems():
            
            location = buffer["attribute_location"]
            
            # find type declaration
            if buffer["ndim"] == 1:
                if buffer["dtype"] == np.float32:
                    vartype = "float"
                else:
                    vartype = "int"
            else:
                # vartype = "vec%d" % buffer["ndim"]
                # HACK: we force 4 dimensions, since everything will work with
                # that
                vartype = "vec%d" % 4 #buffer["ndim"]
                if buffer["dtype"] != np.float32:
                    vartype = "i" + vartype
                    
            # add buffer declaration
            declarations += "layout(location = %d) in %s %s;\n" % \
                                                (location, vartype, name)
        
        # autodeclaration of uniforms
        declarations += "\n// Uniform declarations.\n"
        
        # is_static
        declarations += "uniform bool is_static;\n"
        
        # all uniforms
        for name, uniform in dataset["uniforms"].iteritems():
            
            # HACK: particular case for texture-related uniforms: they
            # are used in the fragment shader instead
            if "tex_sampler" in name:
                continue
                
            typeinfo = _get_value_type(uniform["value"])
            
            # handle array
            tab = ""
            if typeinfo["size"] is not None:
                tab = "[%d]" % typeinfo["size"]
                
            # find type declaration
            if typeinfo["ndim"] == 1:
                if typeinfo["is_float"]:
                    vartype = "float"
                elif typeinfo["is_bool"]:
                    vartype = "bool"
                else:
                    vartype = "int"
            else:
                vartype = "vec%d" % typeinfo["ndim"]
                if not typeinfo["is_float"]:
                    vartype = "i" + vartype
                    
            # add uniform declaration
            declarations += "uniform %s %s%s;\n" % (vartype, name, tab)
            
        declarations += "\n"
            
        # put auto declarations
        vs = vs.replace("%AUTODECLARATIONS%", declarations)
        
        # add version
        vs = "#version 330\n" + vs
        
        # save the modifications
        dataset["vertex_shader"] = vs
                
    def process_fragment_shader_source(self, dataset):
        fs = dataset["fragment_shader"]
        
        # add version
        fs = "#version 330\n" + fs
        
        dataset["fragment_shader"] = fs
                
    def compile_shaders(self, dataset):
        """Compile the shaders.
        
        Arguments:
          * dataset: the dataset object.
        
        """
        # process template for variable autodeclaration
        self.process_vertex_shader_source(dataset)
        self.process_fragment_shader_source(dataset)
        
        vs = dataset["vertex_shader"]
        fs = dataset["fragment_shader"]
        
        # compile vertex shader
        vertex_shader = gl.glCreateShader(gl.GL_VERTEX_SHADER)
        gl.glShaderSource(vertex_shader, vs)
        gl.glCompileShader(vertex_shader)
        
        result = gl.glGetShaderiv(vertex_shader, gl.GL_COMPILE_STATUS)
        # check compilation error
        if not(result):
            msg = "Compilation error:"
            msg += gl.glGetShaderInfoLog(vertex_shader)
            msg += vs
            raise RuntimeError(msg)
        
        # compile fragment shader
        fragment_shader = gl.glCreateShader(gl.GL_FRAGMENT_SHADER)
        gl.glShaderSource(fragment_shader, fs)
        gl.glCompileShader(fragment_shader)
        
        result = gl.glGetShaderiv(fragment_shader, gl.GL_COMPILE_STATUS)
        # check compilation error
        if not(result):
            msg = "Compilation error:"
            msg += gl.glGetShaderInfoLog(fragment_shader)
            msg += fs
            raise RuntimeError(msg)
        
        # create shader program with shaders
        program = gl.glCreateProgram()
        gl.glAttachShader(program, vertex_shader)
        gl.glAttachShader(program, fragment_shader)
        gl.glLinkProgram(program)

        result = gl.glGetProgramiv(program, gl.GL_LINK_STATUS)
        # check linking error
        if not(result):
            msg = "Shader program linking error:"
            msg += gl.glGetProgramInfoLog(program)
            raise RuntimeError(msg)

        dataset["shaders_program"] = program
        
    def activate_shaders(self, dataset):
        """Activate shaders for the rest of the rendering call.
        
        Arguments:
          * dataset: the dataset object.
        
        """
        gl.glUseProgram(dataset["shaders_program"])
        
    def deactivate_shaders(self, dataset):
        """Deactivate shaders for the rest of the rendering call.
        
        This method can be used before calling fixed-pipeline OpenGL commands.
        
        Arguments:
          * dataset: the dataset object.
        
        """
        gl.glUseProgram(0)
        
    def initialize_shaders(self):
        """Initialize shaders in all datasets.
        
        Shader initialization involve using default shader if needed,
        shader compilation, and uniform variables declarations.
        
        """
        for dataset in self.datasets:
            # # special case with one texture and zero buffer
            # if (len(dataset["textures"]) > 0) and (len(dataset["buffers"]) == 0):
                # # show texture
                # self.prepare_single_texture(dataset)
            # set default shader sources
            self.set_default_shaders(dataset)
            # compile shaders
            self.compile_shaders(dataset)
            # initialize all uniforms
            for name in dataset["uniforms"].keys():
                self.define_uniform(name, dataset=dataset)
    
    # Uniform methods
    # ---------------
    def define_uniform(self, name, dataset=None):
        """Define an uniform variable.
        
        Arguments:
          * name: the uniform name, to be used in the shaders.
          * dataset=None: the dataset object, by default the first defined
            dataset.
        
        """
        if dataset is None:
            dataset = self.datasets[0]
        dataset["uniforms"][name]["location"] = gl.glGetUniformLocation(
                dataset["shaders_program"], name)
    
    def update_uniform_values(self, dataset=None, **uniforms):
        """Change an uniform value.
        
        Arguments:
          * **uniforms: keyword arguments with name => value pairs.
          * dataset=None: the dataset object. By default, the first defined
            dataset.
        
        """
        if dataset is None:
            dataset = self.datasets[0]
        for name, value in uniforms.iteritems():
            dataset["uniforms"][name]["value"] = value
            # if True, it means the value has change and needs to be updated
            # on the GPU
            dataset["uniforms"][name]["invalidated"] = True
        
    def validate_uniform_value(self, uniform):
        """Ensure the shape and dtype of the uniform arrays.
        
        Arguments:
          * uniform: the uniform object to validate.
        
        Returns:
          * uniform: the updated uniform object.
        
        """
        if uniform["type"] is np.ndarray:
            if uniform["value"].dtype == np.float64:
                uniform["value"] = enforce_dtype(uniform["value"], np.float32)
            if uniform["value"].dtype == np.int64:
                uniform["value"] = enforce_dtype(uniform["value"], np.int32)
            if uniform["value"].ndim == 1:
                uniform["value"] = np.reshape(uniform["value"], (1, -1))
        return uniform
        
    def update_invalidated_uniforms(self, dataset=None):
        """Update invalidated uniform values.
        
        Only invalidated uniforms are updated, that means that uniforms with 
        unchanged values since the last update are not updated.
        
        Arguments:
          * dataset=None: the dataset, by default the first defined dataset.
          
        """
        if dataset is None:
            dataset = self.datasets[0]
        float_suffix = {True: 'f', False: 'i'}
        array_suffix = {True: 'v', False: ''}
        for name, uniform in dataset["uniforms"].iteritems():
            if not uniform["invalidated"]:
                continue
            typeinfo = _get_value_type(uniform["value"])
            # find function name
            funname = "glUniform%d%s%s" % (typeinfo["ndim"], \
                                           float_suffix[typeinfo["is_float"]], \
                                           array_suffix[typeinfo["size"] is not None])

                                           # find function arguments
            args = (uniform["location"],)
            if typeinfo["size"] is not None:
                args += (typeinfo["size"], uniform["value"])
            elif typeinfo["ndim"] > 1:
                args += uniform["value"]
            elif typeinfo["ndim"] == 1:
                args += (uniform["value"],)
            # get the function from its name
            # print typeinfo, funname
            fun = getattr(gl, funname)
            # call the function
            fun(*args)
            # the uniform value has been updated, no need to update it again 
            # next times, at least until it has been changed again
            uniform["invalidated"] = False

    def transform_view(self):
        """Call GL transformation commands for the interactive navigation."""
        tx, ty = self.interaction_manager.get_translation()
        sx, sy = self.interaction_manager.get_scaling()
        gl.glLoadIdentity()
        gl.glScalef(sx, sy, 1.)
        gl.glTranslatef(tx, ty, 0.)
    
    # Overlay methods
    # ---------------
    def add_transient_overlay(self, name, *args, **kwargs):
        """Add transient overlay.
        
        This function adds an overlay in only one rendering pass.
        It should be called during the life of the widget.
        
        Arguments:
          * name: the name of the overlay. The engine will call the 
           `paint_[name]` method at the next rendering pass.
          * static=False: whether this overlay should have a fixed position
            on the screen or not.
          * *args, **kwargs: arguments of that paint method.
        
        """
        self.transient_overlays.append((name, args, kwargs))
    
    def add_permanent_overlay(self, name, *args, **kwargs):
        """Add permanent overlay.
        
        This function adds an overlay in all rendering passes.
        WARNING: it should only be called at initialization, otherwise
        an infinite number of permanent overlays will be created.
        
        Arguments:
          * name: the name of the overlay. The engine will call the 
           `paint_[name]` method in all rendering passes.
          * static=False: whether this overlay should have a fixed position
            on the screen or not.
          * *args, **kwargs: arguments of that paint method.
        
        """
        self.permanent_overlays.append((name, args, kwargs))
    
    def add_text(self, text, position=(0,0), color=None):
        """Add text as a permanent overlay.
        
        WARNING: To be called at initialization time only.
        
        Arguments:
          * text: a string, or a function returning a string (useful when the
            text needs to be dynamic).
          * position=(0,0): the position of the text in the window relative 
            coordinates (in [-1,1]^2).
          * color=None: the color of the text, yellow by default.
        
        """
        self.add_permanent_overlay("text", text, position=position, color=color)
    
    # Rendering methods
    # -----------------
    def paint_dataset(self, dataset, primitive_type=None, color=None,
                      **buffers_activations):
        """Paint a dataset.
        
        Arguments:
          * dataset: the dataset object, returned by `create_dataset` method.
          * primitive_type=None: a PrimitiveType enum value. By default, 
            the value specified in the dataset creation is used.
          * color=None: the color of the primitives. If None, the color
            specified in the buffer will be used.
          **buffers_activations: for each name, whether to activate or not
            this buffer. It is True by default for all buffers in the dataset.
          
        """
        if primitive_type is None:
            primitive_type = dataset.get("primitive_type", PrimitiveType.Points)
        if color is None:
            color = dataset["color"]
        gl_primitive_type = GL_PRIMITIVE_TYPE_CONVERTER[primitive_type]
        subdata_bounds = dataset["subdata_bounds"]
        
        # by default, choose to activate non specified buffers
        for name, buffer in dataset["buffers"].iteritems():
            if name not in buffers_activations:
                buffers_activations[name] = True
        
        # activate shaders for this dataset
        self.activate_shaders(dataset)
        
        # update invalidated uniforms
        self.update_invalidated_uniforms(dataset)
        
        # use global color if there is no color buffer
        if color is None:
            color = (1, 1, 0)
        if "colors" not in dataset["buffers"] or not buffers_activations["colors"]:
            self._set_color(color)
        
        # go through all slices
        for slice_index in xrange(dataset["slices_count"]):
            # get slice bounds
            slice_bounds = subdata_bounds[slice_index]
            
            # activate or deactivate buffers
            for name, do_activate in buffers_activations.iteritems():
                self.activate_buffer(dataset, name, slice_index, do_activate)
                
            # just use a part of the buffer is bounds has 2 elements
            if len(slice_bounds) == 2:
                gl.glDrawArrays(gl_primitive_type, slice_bounds[0], slice_bounds[1] - slice_bounds[0])
            # use the Multi version of glDrawArrays for painting separate
            # objects in a single OpenGL call (most efficient)
            else:
                first = slice_bounds[:-1]
                count = np.diff(slice_bounds)
                primcount = len(slice_bounds) - 1
                gl.glMultiDrawArrays(gl_primitive_type, first, count, primcount)
        
        # activate textures
        for name, texture in dataset["textures"].iteritems():
            textype = getattr(gl, "GL_TEXTURE_%dD" % texture["ndim"])
            gl.glBindTexture(textype, texture["texture"])
            # gl.glActiveTexture(gl.GL_TEXTURE0 + 0);
        
        # deactivate shaders for this dataset
        self.deactivate_shaders(dataset)
    
    def paint_overlays(self, static=True):
        """Paint permanent and transient overlays.
        
        Arguments:
          * static=True: whether to paint static or non-static overlays.
        
        """
        for overlay in self.permanent_overlays + self.transient_overlays:
            name, args, kwargs = overlay
            static_overlay = kwargs.get("static", True)
            if static_overlay == static:
                getattr(self, "paint_" + name)(*args, **kwargs)    
       
    def paint_text(self, text, position, color=None):
        """Paint a text.
        
        Arguments:
          * text: a string with the text to paint.
          * position: a 2-tuple with the coordinates of the text.
          * color: the color of the text as a 3- or 4- tuple.
          
        """
        if color is not None:
            gl.glColor(*color)
        gl.glRasterPos2f(*position)
        if callable(text):
            text = text()
        try:
            glut.glutBitmapString(glut.GLUT_BITMAP_HELVETICA_12, text)
        except Exception as e:
            log_warn("an error occurred when display text '%s': %s. You probably \
need to install freeglut." % (text, e.message))
        
    def paint_rectangle(self, points, color=None):
        """Paint a rectangle.
        
        Arguments:
          * points: the rectangle coordinates as `(x0, y0, x1, y1)`.
          * color=None: the rectangle fill color as a 3- or 4- tuple.
        
        """
        if color is not None:
            gl.glColor(*color)
        gl.glRectf(*points)
    
    def paint_all(self):
        """Render everything on the screen.
        
        This method is called by paintGL().
        
        """
        # Interactive transformation ON
        # -----------------------------
        self.transform_view()
        
        # plot all datasets
        for dataset in self.datasets:
            self.paint_dataset(dataset)
        
        # paint non static overlays
        self.paint_overlays(static=False)
        
        # Interactive transformation OFF
        # ------------------------------
        # cancel the transformation (static position after this line)
        gl.glLoadIdentity()
        
        # paint static overlays
        self.paint_overlays(static=True)
        
        # remove transient overlays
        self.transient_overlays = []
        
    def updateGL(self):
        """Update rendering."""
        self.parent.updateGL()
        
    # Cleanup methods
    # ---------------
    def cleanup_buffer(self, buffer):
        """Clean up a buffer.
        
        Arguments:
          * buffer: a buffer object.
          
        """
        bfs = [b[0] for b in buffer["vbos"]]
        gl.glDeleteBuffers(len(bfs), bfs)
    
    def cleanup_dataset(self, dataset):
        """Cleanup the dataset by deleting the associated shader program.
        
        Arguments:
          * dataset: the dataset to clean up.
        
        """
        program = dataset["shaders_program"]
        try:
            gl.glDeleteProgram(program)
        except Exception as e:
            log_warn("error when deleting shader program")
        for buffer in dataset["buffers"].itervalues():
            self.cleanup_buffer(buffer)
        
    def cleanup(self):
        """Cleanup all datasets."""
        for dataset in self.datasets:
            self.cleanup_dataset(dataset)
        
    # Methods to be overriden
    # -----------------------
    def initialize(self):
        """Initialize the data. To be overriden.

        This method can make calls to `create_dataset` and `add_*` methods.
        
        """
        pass
