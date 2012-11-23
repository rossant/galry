import numpy as np
import collections

# HACK: if True, activate the OpenGL ES syntax, which is deprecated in the
# desktop version. However with the appropriate #version command in the shader
# most drivers should accept this syntax in the compatibility profile.
# Another option would be to activate/deactivate this variable depending
# on the OpenGL version: TODO
OLDGLSL = True


# Shader templates
# ----------------
if not OLDGLSL:
    VS_TEMPLATE = """
//%GLSL_VERSION_HEADER%
//%GLSL_PRECISION_HEADER%

%VERTEX_HEADER%
void main()
{
    %VERTEX_MAIN%
}

"""

    FS_TEMPLATE = """
//%GLSL_VERSION_HEADER%
//%GLSL_PRECISION_HEADER%

%FRAGMENT_HEADER%
out vec4 out_color;
void main()
{
    %FRAGMENT_MAIN%
}

"""

else:
    VS_TEMPLATE = """
//%GLSL_VERSION_HEADER%
//%GLSL_PRECISION_HEADER%

%VERTEX_HEADER%
void main()
{
    %VERTEX_MAIN%
}

"""

    FS_TEMPLATE = """
//%GLSL_VERSION_HEADER%
//%GLSL_PRECISION_HEADER%

%FRAGMENT_HEADER%
void main()
{
    vec4 out_color = vec4%DEFAULT_COLOR%;
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
    
def _get_uniform_function_name(varinfo):
    """Return the name of the GL function used to update the uniform data.
    
    Arguments:
      * varinfo: the information dictionary about the variable.
    
    Returns:
      * funname: the name of the OpenGL function.
      * args: the tuple of arguments to this function. The data must be 
        appended to this tuple.
    
    """
    # NOTE: varinfo == dict(vartype=vartype, ndim=ndim, size=size)
    float_suffix = {True: 'f', False: 'i'}
    array_suffix = {True: 'v', False: ''}
        
    vartype = varinfo["vartype"]
    ndim = varinfo["ndim"]
    size = varinfo.get("size", None)
    args = ()
    
    # scalar or vector uniform
    if type(ndim) == int or type(ndim) == long:
        # find function name
        funname = "glUniform%d%s%s" % (ndim, \
                                       float_suffix[vartype == "float"], \
                                       array_suffix[size is not None])

        # find function arguments
        if size is not None:
            args += (size,)
            
    # matrix uniform
    elif type(ndim) == tuple:
        # find function name
        funname = "glUniformMatrix%dfv" % (ndim[0])
        args += (1, False,)
        
    return funname, args

    
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


# Shader creator
# --------------
class ShaderCreator(object):
    """Create the shader codes using the defined variables in the visual."""
    def __init__(self):
        self.version_header = '#version 120'
        self.precision_header = 'precision mediump float;'
        
        # list of headers and main code portions of the vertex shader
        self.vs_headers = []
        self.vs_mains = []
        
        # list of headers and main code portions of the fragment shader
        self.fs_headers = []
        self.fs_mains = []
        
        # number of shader snippets to insert at the end
        self.vs_main_end = 0
        self.fs_main_end = 0
        
    def set_variables(self, **kwargs):
        # record all visual variables in the shader creator
        for key, value in kwargs.iteritems():
            setattr(self, key, value)
        
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
            calls to `add_vertex_main`. Or it can be 'end'.
        
        """
        if index == 'end':
            self.vs_main_end += 1
            index = len(self.vs_mains)
        elif index is None:
            index = len(self.vs_mains) - self.vs_main_end
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
        if index == 'end':
            self.fs_main_end += 1
            index = len(self.fs_mains)
        elif index is None:
            index = len(self.fs_mains) - self.fs_main_end
        self.fs_mains.insert(index, code)
    
    def get_shader_codes(self):
        """Build the vertex and fragment final codes, using the declarations
        of all template variables."""
        vs = VS_TEMPLATE
        fs = FS_TEMPLATE
        
        # Vertex header
        vs_header = ""
        vs_header += "".join([get_uniform_declaration(uniform) for uniform in self.uniforms])
        vs_header += "".join([get_attribute_declaration(attribute) for attribute in self.attributes])
        
        # Fragment header
        fs_header = ""
        fs_header += "".join([get_uniform_declaration(uniform) for uniform in self.uniforms])
        fs_header += "".join([get_texture_declaration(texture) for texture in self.textures])
        
        # Varyings
        for varying in self.varyings:
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
        
        # set default color
        fs = fs.replace('%DEFAULT_COLOR%', str(self.default_color))
        
        # replace GLSL version header
        vs = vs.replace('%GLSL_VERSION_HEADER%', self.version_header)
        fs = fs.replace('%GLSL_VERSION_HEADER%', self.version_header)
        
        # replace GLSL precision header
        vs = vs.replace('%GLSL_PRECISION_HEADER%', self.precision_header)
        fs = fs.replace('%GLSL_PRECISION_HEADER%', self.precision_header)
    
        return vs, fs
    
    
# Visual creator
# --------------
class Visual(object):
    """This class defines a visual to be displayed in the scene. It should
    be overriden."""
    def __init__(self, *args, **kwargs):
        self.variables = collections.OrderedDict()
        # initialize the shader creator
        self.shader_creator = ShaderCreator()
        # default options
        self.size = kwargs.pop('size', 0)
        self.default_color = kwargs.pop('default_color', (1., 1., 0., 1.))
        self.bounds = kwargs.pop('bounds', None)
        self.is_static = kwargs.pop('is_static', False)
        self.position_attribute_name = kwargs.pop('position_attribute_name', 'position')
        self.primitive_type = kwargs.pop('primitive_type', 'LINE_STRIP')
        self.constrain_ratio = kwargs.pop('constrain_ratio', False)
        self.constrain_navigation = kwargs.pop('constrain_navigation', False)
        self.visible = kwargs.pop('visible', True)
        # initialize the visual
        self.initialize_default()
        self.initialize(*args, **kwargs)
        # initialize the shader creator
        self.shader_creator.set_variables(
            attributes=self.get_variables('attribute'),
            uniforms=self.get_variables('uniform'),
            textures=self.get_variables('texture'),
            varyings=self.get_variables('varying'),
            default_color = self.default_color,
        )
        # finalize to make sure all variables and shader codes are well defined
        self.finalize()
        # create the shader source codes
        self.vertex_shader, self.fragment_shader = \
            self.shader_creator.get_shader_codes()
        
    # Variable methods
    # ----------------
    def add_foo(self, shader_type, name, **kwargs):
        kwargs['shader_type'] = shader_type
        kwargs['name'] = name
        # default parameters
        kwargs['vartype'] = kwargs.get('vartype', 'float')
        kwargs['size'] = kwargs.get('size', None)
        kwargs['ndim'] = kwargs.get('ndim', 1)
        self.variables[name] = kwargs
        
    def add_attribute(self, name, **kwargs):
        self.add_foo('attribute', name, **kwargs)
        
    def add_uniform(self, name, **kwargs):
        self.add_foo('uniform', name, **kwargs)
        
    def add_texture(self, name, **kwargs):
        self.add_foo('texture', name, **kwargs)
        
    def add_index(self, name, **kwargs):
        self.add_foo('index', name, **kwargs)
        
    def add_varying(self, name, **kwargs):
        self.add_foo('varying', name, **kwargs)
        
    def add_compound(self, name, **kwargs):
        # add the compound as a variable
        self.add_foo('compound', name, **kwargs)
        # process the compound: add the associated data in the corresponding
        # variables
        fun = kwargs['fun']
        data = kwargs['data']
        kwargs = fun(data)
        for name, value in kwargs.iteritems():
            self.variables[name]['data'] = value
        
    def get_variables(self, shader_type=None):
        """Return all variables defined in the visual."""
        if not shader_type:
            return self.variables
        else:
            return [var for (_, var) in self.variables.iteritems() \
                            if var['shader_type'] == shader_type]
        
        
    # Shader methods
    # --------------
    def add_vertex_header(self, *args, **kwargs):
        self.shader_creator.add_vertex_header(*args, **kwargs)
        
    def add_vertex_main(self, *args, **kwargs):
        self.shader_creator.add_vertex_main(*args, **kwargs)
        
    def add_fragment_header(self, *args, **kwargs):
        self.shader_creator.add_fragment_header(*args, **kwargs)
        
    def add_fragment_main(self, *args, **kwargs):
        self.shader_creator.add_fragment_main(*args, **kwargs)
        
        
    # Default visual methods
    # ----------------------
    def initialize_default(self):
        """Default initialization for all child visuals."""
        self.initialize_navigation()
        self.initialize_viewport()
        
    def initialize_viewport(self):
        """Handle window resize in shaders."""
        self.add_uniform('viewport', vartype="float", ndim=2, data=(1., 1.))
        self.add_uniform('window_size', vartype="float", ndim=2, data=(600., 600.))
        if self.constrain_ratio:
            self.add_vertex_main("gl_Position.xy = gl_Position.xy / viewport;", 'end')
        
    def initialize_navigation(self):
        """Handle interactive navigation in shaders."""
        # dynamic navigation
        if not self.is_static:
            self.add_uniform("scale", vartype="float", ndim=2, data=(1., 1.))
            self.add_uniform("translation", vartype="float", ndim=2, data=(0., 0.))
            
            self.add_vertex_header("""
        // Transform a position according to a given scaling and translation.
        vec2 transform_position(vec2 position, vec2 scale, vec2 translation)
        {
        return scale * (position + translation);
        }
            """)
            
        # add transformation only if there is something to display
        # if self.get_variables('attribute'):
        if not self.is_static:
            self.add_vertex_main("""
                gl_Position = vec4(transform_position(%s, scale, translation), 
                               0., 1.);""" % self.position_attribute_name, 'end')
        # static
        else:
            self.add_vertex_main("""
                gl_Position = vec4(%s, 0., 1.);""" % self.position_attribute_name, 'end')
        
        
    # Initialization methods
    # ----------------------
    def initialize(self, *args, **kwargs):
        """The visual should be defined dynamically here."""
    
    def finalize(self):
        """Finalize the template to make sure that shaders are compilable.
        
        This is the place to implement any post-processing algorithm on the
        shader sources, like custom template replacements at runtime.
        
        """
        
        # self.size is a mandatory variable
        assert self.size is not None
        
        # default rendering options
        if self.bounds is None:
            self.bounds = [0, self.size]
        # ensure the type of bounds
        self.bounds = np.array(self.bounds, dtype=np.int32)
    
    
    # Output methods
    # --------------
    def get_dic(self):
        """Return the dict representation of the visual."""
        dic = {
            'visible': self.visible,
            'size': self.size,
            'bounds': self.bounds,
            'primitive_type': self.primitive_type,
            'constrain_ratio': self.constrain_ratio,
            'constrain_navigation': self.constrain_navigation,
            'variables': self.variables.values(),
            'vertex_shader': self.vertex_shader,
            'fragment_shader': self.fragment_shader,
        }
        return dic
        
    
