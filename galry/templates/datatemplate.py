import itertools
import collections
import sys
from ..debugtools import log_info, info_level
from ..primitives import PrimitiveType
import numpy as np

# HACK: Linux in VirtualBox uses OpenGL ES, which requires a special API
# in GLSL. This variable is true when OpenGL ES version 120 is used
# info_level()
# UPDATE: OLDGLSL=True is also necessary for Mac OS X 10.6
OLDGLSL = True
# OLDGLSL = sys.platform != "win32"
# log_info("OLDGLSL=%s" % str(OLDGLSL))


# Shader templates
# ----------------
if not OLDGLSL:
    VS_TEMPLATE = """
%GLSL_VERSION_HEADER%
precision mediump float;

%VERTEX_HEADER%
void main()
{
    %VERTEX_MAIN%
}

"""

    FS_TEMPLATE = """
%GLSL_VERSION_HEADER%
precision mediump float;

%FRAGMENT_HEADER%
out vec4 out_color;
void main()
{
    %FRAGMENT_MAIN%
}

"""



else:
    VS_TEMPLATE = """
%GLSL_VERSION_HEADER%
//precision mediump float;

%VERTEX_HEADER%
void main()
{
    %VERTEX_MAIN%
}

"""

    FS_TEMPLATE = """
%GLSL_VERSION_HEADER%
//precision mediump float;

%FRAGMENT_HEADER%
void main()
{
    vec4 out_color = vec4(1., 1., 1., 1.);
    %FRAGMENT_MAIN%
    gl_FragColor = out_color;
}

"""
    

def _get_shader_type(varinfo):
    """Return the GLSL variable declaration statement from a variable 
    information.
    
    Arguments:
      * varinfo: a dictionary with the information about the variable,
        in particular the type (int/float) and the number of dimensions
        (scalar, vector or matrix).
    
    Returns:
      * declaration: the string containing the variable declaration.
        
    """
    if type(varinfo["ndim"]) == int or type(varinfo["ndim"]) == long:
        if varinfo["ndim"] == 1:
            shader_type = varinfo["vartype"]
        elif varinfo["ndim"] >= 2:
            shader_type = "vec%d" % varinfo["ndim"]
            if varinfo["vartype"] != "float":
                shader_type = "i" + shader_type
    # matrix: (2,2) or (3,3) or (4,4)
    elif type(varinfo["ndim"]) == tuple:
        shader_type = "mat%d" % varinfo["ndim"][0]
    return shader_type
    
# for OLDGLSL: no int possible in attributes or varyings, so we force float
# for uniforms, no problem with int
if OLDGLSL:
    def _get_shader_type_noint(varinfo):
        """Like `_get_shader_type` but only with floats, not int. Used
        in OpenGL ES (OLDGLSL)."""
        if varinfo["ndim"] == 1:
            shader_type = "float"
        elif varinfo["ndim"] >= 2:
            shader_type = "vec%d" % varinfo["ndim"]
        # matrix: (2,2) or (3,3) or (4,4)
        elif type(varinfo["ndim"]) == tuple:
            shader_type = "mat%d" % varinfo["ndim"][0]
        return shader_type
    

# Variable information
# --------------------
# Correspondance between Python data types and GLSL types.    
VARINFO_DICT = {
    # floats
    float: 'float',
    np.float32: 'float',
    np.float64: 'float',
    np.dtype('float32'): 'float',
    np.dtype('float64'): 'float',
    
    # integers
    int: 'int',
    long: 'int',
    np.int32: 'int',
    np.int64: 'int',
    np.dtype('int32'): 'int',
    np.dtype('int64'): 'int',
    
    # booleans
    bool: 'bool',
    np.bool: 'bool',
}

def _get_vartype(scalar):
    """Return the GLSL type of a scalar value."""
    return VARINFO_DICT[type(scalar)]
    
def _get_varinfo(data):
    """Infer variable information (type, number of components) from data.
    
    Arguments:
      * data: any value to be uploaded on the GPU.
    
    Returns:
      * varinfo: a dictionary with the information related to the data type.
      
    """
    
    # handle scalars
    if not hasattr(data, '__len__'):
        return dict(vartype=_get_vartype(data), ndim=1, size=None)
    
    # convert lists into array
    if type(data) == list:
        data = np.array(data)
        
    # handle tuples
    if type(data) == tuple:
        return dict(vartype=_get_vartype(data[0]),
            ndim=len(data), size=None)
    
    # handle arrays
    if isinstance(data, np.ndarray):
        vartype = VARINFO_DICT[data.dtype]
        if data.ndim == 1:
            ndim = 1
            size = len(data)
        elif data.ndim == 2:
            ndim = data.shape[1]
            size = data.shape[0]
        return dict(vartype=vartype, ndim=ndim, size=size)
    
def _get_texinfo(data):
    """Return the texture information of a texture data.
    
    Arguments:
      * data: the texture data as an array.
    
    Returns:
      * texinfo: a dictionary with the information related to the texture data.
      
    """
    ndim = 2
    assert data.ndim == 3
    size = data.shape[:2]
    ncomponents = data.shape[2]
    return dict(size=size, ndim=ndim, ncomponents=ncomponents)
    
def _update_varinfo(varinfo, data):
    """Update incomplete varinfo dict from data.
    
    Arguments:
      * varinfo: a potentially incomplete variable information dictionary.
      * data: the associated data, used to complete the information.
      
    Returns:
      * varinfo: the completed information dictionary.
      
    """
    varinfo_data = _get_varinfo(data)
    if "vartype" not in varinfo:
        varinfo.update(vartype=varinfo_data['vartype'])
    if "ndim" not in varinfo:
        varinfo.update(ndim=varinfo_data['ndim'])
    if "size" not in varinfo:
        varinfo.update(size=varinfo_data['size'])
    return varinfo
    
def _update_texinfo(texinfo, data):
    """Update incomplete texinfo dict from data.
    
    Arguments:
      * texinfo: a potentially incomplete texture information dictionary.
      * data: the associated data, used to complete the information.
      
    Returns:
      * texinfo: the completed information dictionary.
      
    """
    texinfo_data = _get_texinfo(data)
    if "ncomponents" not in texinfo:
        texinfo.update(ncomponents=texinfo_data['ncomponents'])
    if "ndim" not in texinfo:
        texinfo.update(ndim=texinfo_data['ndim'])
    if "size" not in texinfo:
        texinfo.update(size=texinfo_data['size'])
    return texinfo
    
    
# GLSL declaration functions
# --------------------------
def get_attribute_declaration(attribute):
    """Return the GLSL attribute declaration."""
    if not OLDGLSL:
        declaration = "layout(location = %d) in %s %s;\n" % \
                        (attribute["location"],
                         _get_shader_type(attribute), 
                         attribute["name"])
    else:
        declaration = "attribute %s %s;\n" % \
                        (_get_shader_type_noint(attribute), 
                         attribute["name"])
        
    return declaration
    
def get_uniform_declaration(uniform):
    """Return the GLSL uniform declaration."""
    tab = ""
    size = uniform.get("size", None)
    if size is not None:
        tab = "[%d]" % max(1, size)  # ensure that the size is always >= 1
    # add uniform declaration
    declaration = "uniform %s %s%s;\n" % \
        (_get_shader_type(uniform),
         uniform["name"],
         tab)
    return declaration
    
def get_texture_declaration(texture):
    """Return the GLSL texture declaration."""
    declaration = "uniform sampler%dD %s;\n" % (texture["ndim"], texture["name"])
    return declaration
    
def get_varying_declarations(varying):
    """Return the GLSL varying declarations for both vertex and fragment
    shaders."""
    vs_declaration = ""
    fs_declaration = ""
    
    if not OLDGLSL:
        shadertype = _get_shader_type(varying)
    else:
        shadertype = _get_shader_type_noint(varying)
    
    s = "%%s %s %s;\n" % \
        (shadertype, varying["name"])
         
    if not OLDGLSL:
        vs_declaration = s % "out"
        fs_declaration = s % "in"
    else:
        vs_declaration = s % "varying"
        fs_declaration = s % "varying"
    
    if not OLDGLSL:
        if varying.get("flat", None):
            vs_declaration = "flat " + vs_declaration
            fs_declaration = "flat " + fs_declaration
        
    return vs_declaration, fs_declaration


class DataTemplate(object):
    """Describes a particular graphical object.
    
    A data template contains information about the rendering of an object in
    the visual scene, that consists of a homogeneous set of one or multiple
    primitives. Rendering of the data template is eventually done with a single 
    OpenGL command, hence the necessity for homogeneity. Even with a single
    command, multiple independent objects of the same type can be drawn.
    Making a single command is really important for performance, since it is
    the number of rendering commands made every frame that essentially dictates
    the final rendering performance as the number of frames per second.
    
    A template is defined by:
      * a set of variables, or fields, that have a name, a type, and various
        characteristics,
      * vertex and fragment shader source codes that describe how
        data contained in the DataTemplate fields will be converted into
        pixels.
    
    A vertex shader is a small program in a C-like language called GLSL that
    is executed once per vertex. Vertex shaders execute in 
    parallel across all vertices, using the high computational power of the 
    GPU. A vertex shader takes DataTemplate variables as inputs, and
    returns the final position of the vertex.
    
    A fragment shader is also written in GLSL, but executes after the vertex
    shader, and once per pixel. It takes some variables as inputs, as well
    as some output of the vertex shader, and returns the final color of the
    pixel.
    
    There are different types of variables:
      * attributes: an attribute is an array variable of size N. All attributes
        in a given DataTemplate share the same number N. It is essentially
        the number of vertices. Also, there is one execution of the vertex 
        shader per vertex (so N executions), at every rendering call (so
        every frame). Examples of attributes: the position (coordinates of the
        points to render), the color of the points (if each point needs to have
        its own color), etc. Every variable that has one specific value per
        vertex is an attribute.
      * uniforms: an uniform is a global variable, shared by all vertices. It
        may change at every frame, but it is global to the vertex and fragment
        shaders. It can be a scalar, a vector, or an array of scalars or
        vectors. *A uniform variable cannot hold more than 64 KB of data*.
      * varyings: during the rendering process, the vertex shader is executed
        once per vertex. Then, the fragment shader is executed once per pixel
        (pixel of the rendered primitives). Since the fragment shader always
        executes after the vertex shader, the vertex shader can pass 
        information to the fragment shader through varying variables. They
        can be automatically interpolated when the pixels are between 2 or 3
        vertices (hence their names).
      * textures: a texture variable holds a texture data as a 3D array (with
        RGB(A) components) and can be accessed in the fragment shader in
        order to display it.
      * compounds: a particular type of variable that has no counterpart in
        the shaders. A compound variable allows to automatically change
        several template variables according to a high-level value. They exist
        only for convenience for the user. For example, in the TextTemplate,
        where characters are individually positioned on the screen, the
        text variable is a compound variable that affects the texture of the
        characters (i.e. the points), their particular position, etc.
    
    The template is described in the `initialize` method.
    
    """
    def __init__(self):
        """Constructor."""
        # contains all variables
        # the attributes dictionary conserves the definition order 
        # so that the attribute location can automatically be computed
        self.attributes = collections.OrderedDict()
        self.uniforms = {}
        self.textures = {}
        self.varyings = {}
        self.compounds = {}
        
        # list of headers and main code portions of the vertex shader
        self.vs_headers = []
        self.vs_mains = []
        
        # list of headers and main code portions of the fragment shader
        self.fs_headers = []
        self.fs_mains = []
        
        # number of vertices
        self.size = None
        
        # rendering variables
        self.primitive_type = None
        self.bounds = None
        
        # the default color is yellow
        self.default_color = (1., 1., 0., 1.)
    
    def add_attribute(self, name, location=None, **varinfo):
        """Add an attribute variable.
        
        Arguments:
          * name: the name of the attribute. Should be a singular name for
            coherency. This name is used as a variable in the vertex shader,
            where it contains the value of the current vertex.
          * data=None: the initial data. The type information is automatically
            inferred from this initial data. If data is not provided, the type
            information *must* be specified in the following keyword arguments.
          * vartype='float': 'float', 'int' or 'bool'.
          * ndim=1: 1 for a scalar, 2, 3 or 4 for a vector.
          * location=None: the attribute location, should be left to None.
          
        """
        if location is None:
            location = len(self.attributes)
        if "data" in varinfo:
            varinfo = _update_varinfo(varinfo, varinfo["data"])
        self.attributes[name] = dict(name=name, location=location, **varinfo)
        
    def add_uniform(self, name, **varinfo):
        """Add an uniform variable.
        
        Arguments:
          * name: the name of the uniform.
          * data=None: the initial data. The type information is automatically
            inferred from this initial data. If data is not provided, the type
            information *must* be specified in the following keyword arguments.
          * vartype='float': 'float', 'int' or 'bool'.
          * ndim=1: 1 for a scalar, 2, 3 or 4 for a vector.
          
        """
        if "data" in varinfo:
            varinfo = _update_varinfo(varinfo, varinfo["data"])
        self.uniforms[name] = dict(name=name, **varinfo)
        
    def add_varying(self, name, **varinfo):
        """Add a varying variable.
        
        Arguments:
          * name: the name of the varying.
          * data=None: the initial data. The type information is automatically
            inferred from this initial data. If data is not provided, the type
            information *must* be specified in the following keyword arguments.
          * vartype='float': 'float', 'int' or 'bool'.
          * ndim=1: 1 for a scalar, 2, 3 or 4 for a vector.
          
        """
        if "data" in varinfo:
            varinfo = _update_varinfo(varinfo, varinfo["data"])
        self.varyings[name] = dict(name=name, **varinfo)
        
    def add_texture(self, name, **texinfo):
        """Add a texture variable.
        
        Arguments:
          * name: the name of the texture.
          * data=None: the initial data. The type information is automatically
            inferred from this initial data. If data is not provided, the type
            information *must* be specified in the following keyword arguments.
          * ncomponents: the number of texture components (3 for RGB, 4 for
            RGBA with alpha channel).
          * ndim=2: 2D texture only.
          
        """
        if "data" in texinfo:
            texinfo = _update_texinfo(texinfo, texinfo["data"])
        self.textures[name] = dict(name=name, **texinfo)
    
    def add_compound(self, name, **varinfo):
        """Add a compound variable.
        
        Arguments:
          * name: the name of the compound variable.
          * fun: a function that describes the behavior of this compound
            variable. This function accepts a data argument as input, and
            returns a dict with name:value pairs, for each template variable
            that needs to be modified by this compound variable.
          
        """
        self.compounds[name] = dict(name=name, **varinfo)
    
    def add_vertex_header(self, code):
        """Add code in the header of the vertex shader. Generally used to
        define custom functions, to be used in the main shader code."""
        self.vs_headers.append(code)
        
    def add_vertex_main(self, code, index=None):
        """Add code in the main function of the vertex shader.
        At the end of the code, the vec2 variable `position` must have been
        defined, either as an attribute or uniform, or declared in the main
        code. It contains the position of the current vertex.
        Other output variables include `gl_PointSize` for the size of vertices
        in the case when the primitive type is `Points`.
        
        Arguments:
          * code: the GLSL code as a string.
          * index=None: the index of that code snippet in the final main
            function. By default (index=None), the code is appended at the end
            of the main function. With index=0, it is at the beginning of the
            main function. Other integer values may be used when using several
            calls to `add_vertex_main`.
        
        """
        if index is None:
            index = len(self.vs_mains)
        self.vs_mains.insert(index, code)
        
    def add_fragment_header(self, code):
        """Add code in the header of the fragment shader. Generally used to
        define custom functions, to be used in the main shader code."""
        self.fs_headers.append(code)
        
    def add_fragment_main(self, code, index=None):
        """Add code in the main function of the fragment shader.
        At the end of the code, the vec4 variable `out_color` must have been
        defined. It contains the color of the current pixel.
        
        Arguments:
          * code: the GLSL code as a string.
          * index=None: the index of that code snippet in the final main
            function. By default (index=None), the code is appended at the end
            of the main function. With index=0, it is at the beginning of the
            main function. Other integer values may be used when using several
            calls to `add_fragment_main`.
        
        """
        if index is None:
            index = len(self.fs_mains)
        self.fs_mains.insert(index, code)
    
    def get_shader_codes(self):
        """Build the vertex and fragment final codes, using the declarations
        of all template variables."""
        vs = VS_TEMPLATE
        fs = FS_TEMPLATE
        
        # Vertex header
        vs_header = ""
        vs_header += "".join([get_uniform_declaration(uniform) for _, uniform in self.uniforms.iteritems()])
        vs_header += "".join([get_attribute_declaration(attribute) for _, attribute in self.attributes.iteritems()])
        
        # Fragment header
        fs_header = ""
        fs_header += "".join([get_uniform_declaration(uniform) for _, uniform in self.uniforms.iteritems()])
        fs_header += "".join([get_texture_declaration(texture) for _, texture in self.textures.iteritems()])
        
        # Varyings
        for name, varying in self.varyings.iteritems():
            s1, s2 = get_varying_declarations(varying)
            vs_header += s1
            fs_header += s2
        
        vs_header += "".join(self.vs_headers)
        fs_header += "".join(self.fs_headers)
        
        # Integrate shader headers
        vs = vs.replace("%VERTEX_HEADER%", vs_header)
        fs = fs.replace("%FRAGMENT_HEADER%", fs_header)
        
        # Vertex and fragment main code
        vs_main = ""
        vs_main += "".join(self.vs_mains)
        
        fs_main = ""
        fs_main += "".join(self.fs_mains)
        
        # Integrate shader headers
        vs = vs.replace("%VERTEX_MAIN%", vs_main)
        fs = fs.replace("%FRAGMENT_MAIN%", fs_main)
        
        # Make sure there are no Windows carriage returns
        vs = vs.replace(b"\r\n", b"\n")
        fs = fs.replace(b"\r\n", b"\n")
        
        # OLDGLSL does not know the texture function
        # TODO: handle non-2D textures...
        if OLDGLSL:
            fs = fs.replace("texture(", "texture%dD(" % 2)
        
        # TODO: maybe change this as a function of 
        # gl.glGetString(gl.GL_SHADING_LANGUAGE_VERSION) ?
        glslversion = '#version 120'
        vs = vs.replace('%GLSL_VERSION_HEADER%', glslversion)
        fs = fs.replace('%GLSL_VERSION_HEADER%', glslversion)
    
        return vs, fs
    
    def get_initialize_arguments(self, **data):
        """Get the arguments for initialize as a function of the data specified
        in `create_dataset`.
        
        To be overriden.
        
        Arguments:
          * data: keyword arguments with the data passed to `set_data`.
        
        Returns:
          * kwargs: a dictionary of arguments to pass to `initialize`.
        
        """
        return {}
    
    def initialize(self, **kwargs):
        """Initialize the template by making calls to self.add_*.
        
        To be overriden.
        
        """
    
    def finalize(self):
        """Finalize the template to make sure that shaders are compilable.
        
        This is the place to implement any post-processing algorithm on the
        shader sources, like custom template replacements at runtime.
        
        """
        
        # self.size is a mandatory variable
        assert self.size is not None
        
        # default rendering options
        if self.primitive_type is None:
            self.primitive_type = PrimitiveType.LineStrip
        if self.bounds is None:
            self.bounds = [0, self.size]
        self.bounds = np.array(self.bounds, dtype=np.int32)
        
        # default position attribute if no attribute is defined
        if not self.attributes:
            self.add_attribute("position", vartype="float", ndim=2, location=0)
        
        # default fragment code if no fragment code is defined
        if not self.fs_mains:
            self.add_fragment_main("""
            out_color = %s;
            """ % "vec%d%s" % (len(self.default_color), \
                               str(self.default_color)))
    
        # update the list of all template variable names
        vs = ["attributes", "uniforms", "textures", "compounds"]
        self.variable_names = list(itertools.chain(*[getattr(self, v) \
            for v in vs]))
        