

import numpy as np
import OpenGL.GL as gl
from primitives import PrimitiveType, GL_PRIMITIVE_TYPE_CONVERTER
from tools import enforce_dtype
from debugtools import log_debug, log_info, log_warn
from templates.datatemplate import OLDGLSL

__all__ = ['DataLoader']



# Whether to use the array extension of PyOpenGL. Should be False.
USE_PYOPENGL_ARRAY = False

# Converter between Numpy and OpenGL type
NP_GL_TYPE_CONVERTER = {
    np.float32:gl.GL_FLOAT,
    np.int32:gl.GL_INT,
    np.bool:gl.GL_BOOL,
}

DEFAULT_COLOR = (1., 1., 1., 1.)



def _get_vartype(pytype):
    if (pytype == float) | (pytype == np.float32):
        vartype = 'float'
    elif (pytype == int) | (pytype == np.int32):
        vartype = 'int'
    elif pytype == bool:
        vartype = 'bool'
    else:
        vartype = None
    return vartype
  
def _get_varinfo(value):
    """Give information about any numeric variable."""
    # array
    if isinstance(value, np.ndarray):
        vartype = _get_vartype(value.dtype)
        if value.ndim == 1:
            size, ndim = value.size, 1
        elif value.ndim == 2:
            size, ndim = value.shape
        elif value.ndim == 3:
            w, h, ndim = value.shape
            size = w, h
    # tuple
    elif type(value) is tuple:
        vartype = _get_vartype(type(value[0]))
        ndim = len(value)
        size = None
    # scalar value
    else:
        vartype = _get_vartype(type(value))
        ndim = 1
        size = None
    return dict(vartype=vartype, ndim=ndim, size=size)

def validate_data(data):
    if isinstance(data, np.ndarray):
        # enforce 32 bits for arrays of floats
        if data.dtype == np.float64:
            data = enforce_dtype(data, np.float32)
        # enforce 32 bits for arrays of ints
        if data.dtype == np.int64:
            data = enforce_dtype(data, np.int32)
        # enforce 2 dimensions for the array
        if data.ndim == 1:
            data = data.reshape((-1, 1))
    return data
    
def validate_texture(data):
    return np.array(255 * data, dtype=np.uint8)
    
    
# VBO functions
# -------------

# Maximum size of a VBO, generally 65k. You might try to increase it
# in order to improve performance, but be very careful since no error will
# be raised if you cross the limit: all values defined after that limit
# will be zero, so you might just have very weird results! Make sure to test.
MAX_VBO_SIZE = 65000

def create_vbo(data, location=None):
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
        # gl.glBindBuffer(gl.GL_ARRAY_BUFFER, buffer)
        bind_vbo(buffer, location=location)
        gl.glBufferData(gl.GL_ARRAY_BUFFER, data, 
                        gl.GL_DYNAMIC_DRAW)
    return buffer
    
def bind_vbo(buffer, location=None):
    """Bind a VBO.
    
    Use this function before using a VBO (like updating the data or rendering
    it).
    
    Arguments:
      * buffer: the object returned by `create_vbo`.
      
    """
    if USE_PYOPENGL_ARRAY:
        buffer.bind()
    else:
        if OLDGLSL:
            assert location is not None
            gl.glEnableVertexAttribArray(location)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, buffer)

def update_vbo(buffer, newdata, onset=None, location=None):
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
    bind_vbo(buffer, location=location)
    gl.glBufferSubData(gl.GL_ARRAY_BUFFER, onset, newdata)
        
        
def activate_buffer(vbo, location, ndim, do_activate):
    # TODO: refactor this
    bind_vbo(vbo, location=location)
    if do_activate:
        gl.glEnableVertexAttribArray(location)
        gl.glVertexAttribPointer(location, ndim, gl.GL_FLOAT, gl.GL_FALSE, 0, None)
    else:
        gl.glDisableVertexAttribArray(location)
        
        

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

def _slice_data(data, slices=None):
    """Slice an array according to the dataset slices.
    
    Arguments:
      * data: a Nx2 array.
      * slices: the slices returned by `_get_slices`, or `None` (in which
        case they will be computed).
      
    Returns:
      * data_sliced: a list of triplets `(subdata, position, slice_size)`.
      
    """
    if slices is None:
        slices = _get_slices(data.shape[0])
    return [(data[position:position+size,:], position, size) for position, size in slices]

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
    
def _set_drawing_size( primitive_type, size):
    """Set the drawing size.
    
    Arguments:
      * primitive_type: a PrimitiveType enum value.
      * size: the size of the point or line (1 by default).
      
    """
    if primitive_type == PrimitiveType.Points:
        gl.glPointSize(size)
    elif primitive_type == PrimitiveType.LineStrip:
        gl.glLineWidth(size)
    
def _set_vbo(vbo, location, ndim, dtype=None, gltype=None):
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
    bind_vbo(vbo, location=location)
    gl.glEnableVertexAttribArray(location)
    gl.glVertexAttribPointer(location, ndim, gltype, gl.GL_FALSE, 0, None)
    



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




class DataLoader(object):
    def __init__(self, size, template=None, bounds=None):
        self.size = size
        self.template = template
        
        self.attributes = None
        self.uniforms = None
        self.textures = None
        self.compounds = None
        
        self.invalidated = {}
        
        self.bounds = bounds
        self.slices_count = int(np.ceil(size / float(MAX_VBO_SIZE)))
        self.slices = _get_slices(size)
        self.subdata_bounds = [_slice_bounds(bounds, pos, size) for pos, size in self.slices]
        
        self.initialize_variables()
        
        
    def initialize_variables(self):
        # initialize "uniforms", "attributes" or "textures" keys
        # in the dataset, where each value is itself a dict with
        # all uniforms/attributes/textures.
        self.variables = {}
        alldata = {}
        for variable in ["attributes", "uniforms", "textures", "compounds"]:
            vardic = {}
            tpl = self.template
            for name, dic in getattr(tpl, variable).iteritems():
                self.variables[name] = variable
                # copy the variables in the template to the dataset
                vardic[name] = dict(**dic)
                # if "default" in dic:
                if "data" in dic:
                    alldata[name] = dic["data"]
                # add uniform invalidation
                # if variable == "uniforms":
                    # vardic[name]["invalidated"] = True
                # if variable != "compounds":
                    # self.invalidated[name] = True
            setattr(self, variable, vardic)
        
        self.set_data(**alldata)
        
    def set_data(self, **kwargs):
        """Set attribute/uniform/texture data. To be called at initialize time.
        No data is sent on the GPU here.
        
        """
        tpl = self.template
        
        # special case: primitive_type
        if "primitive_type" in kwargs:
            tpl.set_rendering_options(primitive_type=kwargs["primitive_type"])
            del kwargs["primitive_type"]
        
        kwargs2 = kwargs.copy()
        # first, find possible compounds and add them to kwargs
        for name, data in kwargs2.iteritems():
            if self.variables[name] == "compounds":
                fun = self.compounds[name]["fun"]
                kwargs.update(**fun(data))
                del kwargs[name]
        
        # now, we have the actual list of variables to update
        for name, data in kwargs.iteritems():
            # print "hey", name, data
            # variable is attribute, uniform or texture
            variable = self.variables[name]
            dic = getattr(self, variable)[name]
            if variable == "textures":
                data = validate_texture(data)
            else:
                data = validate_data(data)
            # the special variable property "preprocess" is used to preprocess
            # the data given in set_data
            if "preprocess" in variable:
                data = dic["preprocess"](data)
            dic["data"] = data
            # if variable == "uniforms":
                # dic["invalidated"] = True
            # print id(self), name, getattr(self, variable)[name].get("data", None)
            # we tell the loader that the data of name has changed and that is
            # should be updated later
            self.invalidated[name] = True
        # return [name for name in kwargs.keys()]


        
    def upload_attribute_data(self, name, mask=None):  
        # print self.template.attributes["position"]  
        bf = self.attributes[name]
        data = bf.get("data", None)
        if data is None:
            raise RuntimeError("No data found for attribute %s, skipping data uploading"\
                % name)
            # return
        data_sliced = _slice_data(data, self.slices)
        # add data
        if "vbos" not in bf:
            if not OLDGLSL:
                bf["vbos"] = [(create_vbo(subdata), pos, size) for subdata, pos, size in data_sliced]
            else:
                # print bf["location"], self.template.attributes["position"] , name
                bf["vbos"] = [(create_vbo(subdata, bf["location"]), pos, size) for subdata, pos, size in data_sliced]
        # or update data
        else:
            # default mask
            if mask is None:
                mask = np.ones(self.size, dtype=bool)
            # is the current subVBO within the given [onset, offset]?
            within = False
            # update VBOs
            for slice_index in xrange(len(data_sliced)):
                newsubdata, pos, slice_size = data_sliced[slice_index]
                vbo, _, _ = bf["vbos"][slice_index]
                # subdata_bounds is the bounds (as a list) for the current subdata
                subdata_bounds = self.subdata_bounds[slice_index]
                # mask of updated indices in the subVBO
                submask = mask[pos:pos + slice_size]
                # if there is at least one True in the slice mask (submask)
                if submask.any():
                    # this subVBO contains updated indices
                    subonset = submask.argmax()
                    suboffset = len(submask) - 1 - submask[::-1].argmax()
                    update_vbo(vbo, newsubdata[subonset:suboffset + 1], subonset,
                        location=bf["location"])
        
    def upload_uniform_data(self, name):
        # define GL uniform
        uniform = self.uniforms[name]
        if "location" not in uniform:
            uniform["location"] = gl.glGetUniformLocation(
                self.shaders_program, name)
    
        float_suffix = {True: 'f', False: 'i'}
        array_suffix = {True: 'v', False: ''}
        
        # if not uniform["invalidated"]:
            # return
            
        vartype = uniform["vartype"]
        size = uniform.get("size", None)
        
        data = uniform.get("data", None)
        if data is None:
            raise RuntimeError("No data found for uniform %s, skipping data uploading"\
                % name)
            # return
        
        # TODO: register function name at initialization time
        
        # find function name
        funname = "glUniform%d%s%s" % (uniform["ndim"], \
                                       float_suffix[vartype == "float"], \
                                       array_suffix[size is not None])

        # find function arguments
        args = (uniform["location"],)
        if size is not None:
            args += (size, data)
        elif uniform["ndim"] > 1:
            args += data
        elif uniform["ndim"] == 1:
            args += (data,)
        # get the function from its name
        fun = getattr(gl, funname)
        # call the function
        fun(*args)
        # the uniform value has been updated, no need to update it again 
        # next times, at least until it has been changed again
        uniform["invalidated"] = False

    def upload_texture_data(self, name):
        texture = self.textures[name]
        # add data
        if "location" not in texture:
            texture["location"] = create_texture(texture["data"], texture["size"], texture["ndim"], 
                            texture["ncomponents"])
        # or update data
        else:
            update_texture(texture["location"], texture["data"], texture["size"], 
                            texture["ndim"], texture["ncomponents"])
        
        
    # def upload_variables(self, *names):
        # print names
        # # print self.template.attributes["position"]
        # for name in names:
            # var = self.variables[name]
            # if var == "uniforms" or var == "compounds":
                # continue
            # getattr(self, "upload_%s_data" % var[:-1])(name)
            
    def upload_data(self):
        """Upload all invalidated data."""
        # print names
        # print self.template.attributes["position"]
        # we go through all invalidated data
        names = [k for (k, v) in self.invalidated.iteritems() if v]
        log_info("uploading " + ", ".join(names))
        for name in names:
            var = self.variables[name]
            # if var == "uniforms" or var == "compounds":
                # continue
            getattr(self, "upload_%s_data" % var[:-1])(name)
            self.invalidated[name] = False
 
    # def upload_invalidated_uniform_data(self):
        # for name, uniform in self.uniforms.iteritems():
            # self.upload_uniform_data(name)
 
    # GL shader methods
    # -----------------
    def compile_shaders(self):
        """Compile the shaders.
        
        Arguments:
          * dataset: the dataset object.
        
        """
        
        vs, fs = self.template.get_shader_codes()
        
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
        
        
        # OLDGLSL: explicitely link attribute locations to names
        if OLDGLSL:
            for name, attr in self.template.attributes.iteritems():
                attr["location"] = gl.glGetAttribLocation(program, name)
                self.attributes[name]["location"] = gl.glGetAttribLocation(program, name)
        
        self.shaders_program = program
        
    def activate_shaders(self):
        """Activate shaders for the rest of the rendering call.
        
        Arguments:
          * dataset: the dataset object.
        
        """
        gl.glUseProgram(self.shaders_program)
        
    def deactivate_shaders(self):
        """Deactivate shaders for the rest of the rendering call.
        
        This method can be used before calling fixed-pipeline OpenGL commands.
        
        Arguments:
          * dataset: the dataset object.
        
        """
        gl.glUseProgram(0)
        
        
