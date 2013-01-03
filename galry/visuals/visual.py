import numpy as np
import collections
from textwrap import dedent

__all__ = ['OLDGLSL', 'RefVar', 'Visual', 'CompoundVisual']

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
    %FRAG%
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
    assert data.ndim == 3
    size = data.shape[:2]
    if size[0] == 1:
        ndim = 1
    elif size[0] > 1:
        ndim = 2
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
        # self.vs_headers = []
        # self.vs_mains = []
        self.headers = {'vertex': [], 'fragment': []}
        self.mains = {'vertex': [], 'fragment': []}
        
        self.fragdata = None
        
    def set_variables(self, **kwargs):
        # record all visual variables in the shader creator
        for key, value in kwargs.iteritems():
            setattr(self, key, value)
        
        
    # Header-related methods
    # ----------------------
    def add_header(self, code, shader=None):
        code = dedent(code)
        self.headers[shader].append(code)
        
    def add_vertex_header(self, code):
        """Add code in the header of the vertex shader. Generally used to
        define custom functions, to be used in the main shader code."""
        self.add_header(code, 'vertex')
        
    def add_fragment_header(self, code):
        """Add code in the header of the fragment shader. Generally used to
        define custom functions, to be used in the main shader code."""
        self.add_header(code, 'fragment')
        
    def get_header(self, shader=None):
        header = "".join(self.headers[shader])
        if shader == 'vertex':
            header += "".join([get_uniform_declaration(uniform) for uniform in self.uniforms])
            header += "".join([get_attribute_declaration(attribute) for attribute in self.attributes])
        elif shader == 'fragment':
            header += "".join([get_uniform_declaration(uniform) for uniform in self.uniforms])
            header += "".join([get_texture_declaration(texture) for texture in self.textures])
        return header
        
        
    # Main-related methods
    # --------------------
    def add_main(self, code, shader=None, name=None, after=None, position=None):
        if name is None:
            name = '%s_main_%d' % (shader, len(self.mains[shader]))
        code = dedent(code)
        self.mains[shader].append(dict(name=name, code=code, after=after, position=position))
    
    def add_vertex_main(self, *args, **kwargs):
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
        kwargs['shader'] = 'vertex'
        self.add_main(*args, **kwargs)
        
    def add_fragment_main(self, *args, **kwargs):
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
        kwargs['shader'] = 'fragment'
        self.add_main(*args, **kwargs)
    
    def get_main(self, shader=None):
        mains = self.mains[shader]
        # first, all snippet names which do not have 'after' keyword, and which are not last
        order = [m['name'] for m in mains if m['after'] is None and m['position'] is None]
        # then, those which do not have 'after' keyword, but are last
        order += [m['name'] for m in mains if m['after'] is None and m['position'] == 'last']
        # then, get the final order with the "after" snippets
        for m in mains:
            if m['after']:
                # which index for "after"?
                if m['after'] in order:
                    index = order.index(m['after'])
                else:
                    index = len(order) - 1
                order.insert(index + 1, m['name'])
        # finally, get the final code
        main = ""
        for name in order:
            main += [m['code'] for m in mains if m['name'] == name][0]
        return main
    
    
    # Shader creation
    # ---------------
    def set_fragdata(self, fragdata):
        self.fragdata = fragdata
    
    def get_shader_codes(self):
        """Build the vertex and fragment final codes, using the declarations
        of all template variables."""
        vs = VS_TEMPLATE
        fs = FS_TEMPLATE
        
        # Shader headers
        vs_header = self.get_header('vertex')
        fs_header = self.get_header('fragment')
        
        # Varyings
        for varying in self.varyings:
            s1, s2 = get_varying_declarations(varying)
            vs_header += s1
            fs_header += s2
        
        # vs_header += "".join(self.vs_headers)
        # fs_header += "".join(self.fs_headers)
        
        # Integrate shader headers
        vs = vs.replace("%VERTEX_HEADER%", vs_header)
        fs = fs.replace("%FRAGMENT_HEADER%", fs_header)
        
        # Vertex and fragment main code
        vs_main = self.get_main('vertex')
        fs_main = self.get_main('fragment')
        
        # Integrate shader headers
        vs = vs.replace("%VERTEX_MAIN%", vs_main)
        fs = fs.replace("%FRAGMENT_MAIN%", fs_main)
        
        # frag color or frag data
        if self.fragdata is None:
            fs = fs.replace('%FRAG%', """gl_FragColor = out_color;""")
        else:
            fs = fs.replace('%FRAG%', """gl_FragData[%d] = out_color;""" % self.fragdata)
        
        # Make sure there are no Windows carriage returns
        vs = vs.replace(b"\r\n", b"\n")
        fs = fs.replace(b"\r\n", b"\n")
        
        # OLDGLSL does not know the texture function
        if not OLDGLSL:
            fs = fs.replace("texture1D(", "texture(" % 2)
            fs = fs.replace("texture2D(", "texture(" % 2)
        
        # set default color
        fs = fs.replace('%DEFAULT_COLOR%', str(self.default_color))
        
        # replace GLSL version header
        vs = vs.replace('%GLSL_VERSION_HEADER%', self.version_header)
        fs = fs.replace('%GLSL_VERSION_HEADER%', self.version_header)
        
        # replace GLSL precision header
        vs = vs.replace('%GLSL_PRECISION_HEADER%', self.precision_header)
        fs = fs.replace('%GLSL_PRECISION_HEADER%', self.precision_header)
    
        return vs, fs
    
    
    
# Reference variable
# ------------------
class RefVar(object):
    """Defines a reference variable to an attribute of any visual.
    This allows one attribute value to refer to the same memory buffer
    in both system and graphics memory."""
    def __init__(self, visual, variable):
        self.visual = visual
        self.variable = variable
        
    def __repr__(self):
        return "<reference variable to '%s.%s'>" % (self.visual, self.variable)
        
    
# Visual creator
# --------------
class BaseVisual(object):
    def __init__(self, scene, *args, **kwargs):
        self.scene = scene
        # default options
        self.kwargs = self.extract_common_parameters(**kwargs)
        
    def extract_common_parameters(self, **kwargs):
        self.size = kwargs.pop('size', 0)
        self.default_color = kwargs.pop('default_color', (1., 1., 0., 1.))
        self.bounds = kwargs.pop('bounds', None)
        self.is_static = kwargs.pop('is_static', False)
        self.position_attribute_name = kwargs.pop('position_attribute_name', 'position')
        self.primitive_type = kwargs.pop('primitive_type', None)
        self.constrain_ratio = kwargs.pop('constrain_ratio', False)
        self.constrain_navigation = kwargs.pop('constrain_navigation', False)
        self.visible = kwargs.pop('visible', True)
        # self.normalize = kwargs.pop('normalize', None)
        self.framebuffer = kwargs.pop('framebuffer', 0)
        self.fragdata = kwargs.pop('fragdata', None)
        return kwargs
        
    
class Visual(BaseVisual):
    """This class defines a visual to be displayed in the scene. It should
    be overriden."""
    def __init__(self, scene, *args, **kwargs):
        super(Visual, self).__init__(scene, *args, **kwargs)
        kwargs = self.kwargs
        self.variables = collections.OrderedDict()
        self.options = {}
        self.is_position_3D = False
        self.depth = None
        # initialize the shader creator
        self.shader_creator = ShaderCreator()
        self.reinitialization = False
        kwargs = self.resolve_references(**kwargs)
        # initialize the visual
        self.initialize(*args, **kwargs)
        self.initialize_default()
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
    
    
    # Reference variables methods
    # ---------------------------
    def get_visuals(self):
        """Return all visuals defined in the scene."""
        return self.scene['visuals']
        
    def get_visual(self, name):
        """Return a visual dictionary from its name."""
        visuals = [v for v in self.get_visuals() if v.get('name', '') == name]
        if not visuals:
            return None
        return visuals[0]
        
    def get_variable(self, name, visual=None):
        """Return a variable by its name, and for any given visual which 
        is specified by its name."""
        # get the variables list
        if visual is None:
            variables = self.variables.values()
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
       
    def resolve_references(self, **kwargs):
        """Resolve all references in the visual initializer."""
        # deal with reference variables
        self.references = {}
        # record all reference variables in the references dictionary
        for name, value in kwargs.iteritems():
            if isinstance(value, RefVar):
                self.references[name] = value
                # then, resolve the reference value on the CPU only, so that
                # it can be used in initialize(). The reference variable will
                # still be registered in the visual dictionary, for later use
                # by the GL renderer.
                kwargs[name] = self.resolve_reference(value)['data']
        return kwargs
    
    
    # Reinitialization methods
    # ------------------------
    def reinit(self):
        """Begin a reinitialization process, where paint_manager.initialize()
        is called after initialization. The visual initializer is then
        called again, but it is only used to update the data, not to create
        the visual variables and the shader, which have already been created
        in the first place."""
        self.data_updating = {}
        self.reinitialization = True
        # force the bounds to be defined again
        self.bounds = None
       
    def get_data_updating(self):
        """Return the dictionary with the updated variable data."""
        # add some special keywords, if they are specified in self.initialize
        special_keywords = ['size', 'bounds', 'primitive_type']
        for keyword in special_keywords:
            val = getattr(self, keyword)
            if val is not None and keyword not in self.data_updating:
                self.data_updating[keyword] = val
        return self.data_updating
       
        
    # Variable methods
    # ----------------
    def add_foo(self, shader_type, name, **kwargs):
        # for reinitialization, just record the data
        if self.reinitialization:
            if 'data' in kwargs:
                self.data_updating[name] = kwargs['data']
            return
        # otherwise, add the variable normally
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
        # NEW: add texture index
        # if 'index' not in kwargs:
            # kwargs['index'] = len(self.get_variables('texture'))
        self.add_foo('texture', name, **kwargs)
        
    def add_framebuffer(self, name, **kwargs):
        # NEW: add texture index
        # if 'index' not in kwargs:
            # kwargs['index'] = len(self.get_variables('texture'))
        self.add_foo('framebuffer', name, **kwargs)
        
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
        
    
    # Option methods
    # --------------
    def add_options(self, **kwargs):
        self.options.update(kwargs)
        
    # def add_normalizer(self, name, viewbox=None):
        # """Add a data normalizer for attribute 'name'."""
        # # option_name = '%s_normalizer' % name
        # # self.add_option(option_name=(name, viewbox))
        # if 'normalizers' not in self.options:
            # self.options['normalizers'] = {}
        # self.options['normalizers'][name] = viewbox
        
        
    # Variable methods
    # ----------------
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
        if not self.reinitialization:
            self.shader_creator.add_vertex_header(*args, **kwargs)
        
    def add_vertex_main(self, *args, **kwargs):
        if not self.reinitialization:
            self.shader_creator.add_vertex_main(*args, **kwargs)
        
    def add_fragment_header(self, *args, **kwargs):
        if not self.reinitialization:
            self.shader_creator.add_fragment_header(*args, **kwargs)
        
    def add_fragment_main(self, *args, **kwargs):
        if not self.reinitialization:
            self.shader_creator.add_fragment_main(*args, **kwargs)
        
    def set_fragdata(self, fragdata):
        self.shader_creator.set_fragdata(fragdata)
        
        
    # Default visual methods
    # ----------------------
    def initialize_default(self):
        """Default initialization for all child visuals."""
        self.initialize_navigation()
        self.initialize_viewport()
        
    def initialize_viewport(self):
        """Handle window resize in shaders."""
        self.add_uniform('viewport', vartype="float", ndim=2, data=(1., 1.))
        self.add_uniform('window_size', vartype="float", ndim=2)#, data=(600., 600.))
        if self.constrain_ratio:
            self.add_vertex_main("gl_Position.xy = gl_Position.xy / viewport;",
                position='last', name='viewport')
        
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
            
        if not self.is_static:            
            pos = "transform_position(%s.xy, scale, translation)" % self.position_attribute_name
        else:
            pos = "%s.xy" % self.position_attribute_name
        
        if self.is_position_3D:
            vs = """gl_Position = vec4(%s, %s.z, 1.);""" % (pos,
                self.position_attribute_name)
        else:
            vs = """gl_Position = vec4(%s, 0., 1.);""" % (pos)
        
        if self.depth is not None:
            vs += """gl_Position.z = %.4f;""" % self.depth
        
        self.add_vertex_main(vs, position='last', name='navigation')
        
        
    # Initialization methods
    # ----------------------
    def initialize(self, *args, **kwargs):
        """The visual should be defined here."""
    
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
    
        if self.fragdata is not None:
            self.set_fragdata(self.fragdata)
    
        if self.primitive_type is None:
            self.primitive_type = 'LINE_STRIP'
    
    
    # Output methods
    # --------------
    def get_variables_list(self):
        """Return the list of variables, to be used in the output dictionary
        containing all the visual information."""
        variables = self.variables.values()
        # handle reference variables
        for variable in variables:
            name = variable['name']
            if name in self.references:
                variable['data'] = self.references[name]
        return variables
    
    def get_dic(self):
        """Return the dict representation of the visual."""
        dic = {
            'size': self.size,
            'bounds': self.bounds,
            'visible': self.visible,
            'is_static': self.is_static,
            'options': self.options,
            'primitive_type': self.primitive_type,
            'constrain_ratio': self.constrain_ratio,
            'constrain_navigation': self.constrain_navigation,
            'framebuffer': self.framebuffer,
            # 'beforeclear': self.beforeclear,
            'variables': self.get_variables_list(),
            'vertex_shader': self.vertex_shader,
            'fragment_shader': self.fragment_shader,
        }
        return dic
        
    
class CompoundVisual(BaseVisual):
    def __init__(self, scene, *args, **kwargs):
        # super(CompoundVisual, self).__init__(scene, *args, **kwargs)
        self.visuals = []
        self.name = kwargs.pop('name')
        self.initialize(*args, **kwargs)
    
    def add_visual(self, visual_class, *args, **kwargs):
        name = kwargs.get('name', 'visual%d' % len(self.visuals))
        # prefix the visual name with the compound name
        kwargs['name'] = self.name + "_" + name
        self.visuals.append((visual_class, args, kwargs))
    
    def initialize(self, *args, **kwargs):
        pass
        
        
        