import itertools
import collections
import sys
from ..debugtools import log_info, info_level
from ..primitives import PrimitiveType
import numpy as np

# HACK: Linux in VirtualBox uses OpenGL ES, which requires a special API
# in GLSL. This variable is true when OpenGL ES version 120 is used
# info_level()
# OLDGLSL = sys.platform != "win32"
OLDGLSL = False
log_info("OLDGLSL=%s" % str(OLDGLSL))





if not OLDGLSL:
    VS_TEMPLATE = """
#version 330
precision mediump float;

%VERTEX_HEADER%
void main()
{
    %VERTEX_MAIN%
}

"""

    FS_TEMPLATE = """
#version 330
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
#version 120
//precision mediump float;

%VERTEX_HEADER%
void main()
{
    %VERTEX_MAIN%
}

"""

    FS_TEMPLATE = """
#version 120
//precision mediump float;

%FRAGMENT_HEADER%
void main()
{
    vec4 out_color = vec4(1., 1., 1., 1.);
    %FRAGMENT_MAIN%
    gl_FragColor = out_color;
}

"""
    

    
    
    
# if not OLDGLSL:
def _get_shader_type(varinfo):
    if type(varinfo["ndim"]) == int:
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
        if varinfo["ndim"] == 1:
            shader_type = "float"
        elif varinfo["ndim"] >= 2:
            shader_type = "vec%d" % varinfo["ndim"]
        # matrix: (2,2) or (3,3) or (4,4)
        elif type(varinfo["ndim"]) == tuple:
            shader_type = "mat%d" % varinfo["ndim"][0]
        return shader_type
    
    
def _get_shader_vector(vec):
    return "vec%d%s" % (len(vec), str(vec))
    


    
VARINFO_DICT = {
    float: 'float',
    np.float32: 'float',
    np.float64: 'float',
    np.dtype('float32'): 'float',
    np.dtype('float64'): 'float',
    
    int: 'int',
    np.int32: 'int',
    np.int64: 'int',
    np.dtype('int32'): 'int',
    np.dtype('int64'): 'int',
    
    bool: 'bool',
    np.bool: 'bool',

}

def _get_vartype(scalar):
    return VARINFO_DICT[type(scalar)]
    
def _get_varinfo(data):
    """Infer variable information (type, number of components) from data."""
    
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
    ndim = 2
    assert data.ndim == 3
    size = data.shape[:2]
    ncomponents = data.shape[2]
    return dict(size=size, ndim=ndim, ncomponents=ncomponents)
    
def _update_varinfo(varinfo, data):
    """Update incomplete varinfo dict from data."""
    varinfo_data = _get_varinfo(data)
    if "vartype" not in varinfo:
        varinfo.update(vartype=varinfo_data['vartype'])
    if "ndim" not in varinfo:
        varinfo.update(ndim=varinfo_data['ndim'])
    if "size" not in varinfo:
        varinfo.update(size=varinfo_data['size'])
    return varinfo
    
def _update_texinfo(texinfo, data):
    """Update incomplete texinfo dict from data."""
    texinfo_data = _get_texinfo(data)
    if "ncomponents" not in texinfo:
        texinfo.update(ncomponents=texinfo_data['ncomponents'])
    if "ndim" not in texinfo:
        texinfo.update(ndim=texinfo_data['ndim'])
    if "size" not in texinfo:
        texinfo.update(size=texinfo_data['size'])
    return texinfo
    

    
    
    
    
def get_attribute_declaration(attribute):
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
    tab = ""
    size = uniform.get("size", None)
    if size is not None:
        tab = "[%d]" % size
    # add uniform declaration
    declaration = "uniform %s %s%s;\n" % \
        (_get_shader_type(uniform),
         uniform["name"],
         tab)
    return declaration
    
def get_texture_declaration(texture):
    declaration = "uniform sampler%dD %s;\n" % (texture["ndim"], texture["name"])
    return declaration
    
def get_varying_declarations(varying):
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
    def __init__(self):#, size=None):
        self.attributes = collections.OrderedDict()
        self.uniforms = {}
        self.textures = {}
        self.varyings = {}
        self.compounds = {}
        
        self.vs_headers = []
        self.vs_mains = []
        
        self.fs_headers = []
        self.fs_mains = []
        
        # self.default_data = {}
        
        # self.size = size
        self.size = None
        self.primitive_type = None
        self.bounds = None #[0, size]
        self.default_color = (1., 1., 0., 1.)
    
    # def set_size(self, size):
        # self.size = size
    
    # def set_default_data(self, name, data):
        # self.default_data[name] = data
    
    def add_attribute(self, name, location=None, **varinfo):
        if location is None:
            location = len(self.attributes)
        if "data" in varinfo:
            varinfo = _update_varinfo(varinfo, varinfo["data"])
        self.attributes[name] = dict(name=name, location=location, **varinfo)
        # if default is not None:
            # self.set_default_data(**{name:default})
        
    def add_uniform(self, name, **varinfo): #data=None, **varinfo):
        if "data" in varinfo:
            varinfo = _update_varinfo(varinfo, varinfo["data"])
        self.uniforms[name] = dict(name=name, **varinfo)
        # if default is not None:
            # self.set_default_data(**{name:default})
        
    def add_varying(self, name, **varinfo): #data=None, **varinfo):
        if "data" in varinfo:
            varinfo = _update_varinfo(varinfo, varinfo["data"])
        self.varyings[name] = dict(name=name, **varinfo)
        # if default is not None:
            # self.set_default_data(**{name:default})
        
    def add_texture(self, name, **texinfo):#data=None, #location=None,
        # if location is None:
            # location = len(self.textures)
        if "data" in texinfo:
            texinfo = _update_texinfo(texinfo, texinfo["data"])
        self.textures[name] = dict(name=name, #location=location,
            **texinfo)
        # if default is not None:
            # self.set_default_data(**{name:default})
    
    def add_compound(self, name, **varinfo):
        self.compounds[name] = dict(name=name, **varinfo)
    
    def add_vertex_header(self, code):
        self.vs_headers.append(code)
        
    def add_vertex_main(self, code, index=None):
        if index is None:
            index = len(self.vs_mains)
        self.vs_mains.insert(index, code)
        
    def add_fragment_header(self, code):
        self.fs_headers.append(code)
        
    def add_fragment_main(self, code, index=None):
        if index is None:
            index = len(self.fs_mains)
        self.fs_mains.insert(index, code)
    
    # def set_default_color(self, default_color=None): 
        # if default_color is not None:
            # self.default_color = default_color
    
    # def set_rendering_options(self, primitive_type=None, bounds=None): 
        # if primitive_type is not None:
            # self.primitive_type = primitive_type
        # if bounds is not None:
            # self.bounds = bounds
    
    def get_shader_codes(self):
        
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
    
        # log_info(vs)
        # log_info(fs)
        
        return vs, fs
    
    # def set_default_data(self, **kwargs):
        # """Set default data for template variables."""
        # for name, data in kwargs.iteritems():
            # self.default_data[name] = data
    
    def get_initialize_arguments(self, **data):
        """Get the arguments for initialize as a function of the data specified
        in `create_dataset`.
        
        To be overriden.
        
        Arguments:
          * data: keyword arguments with the data to pass to `set_data`.
        
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
        
        assert type(self.size) == int
        # assert self.size is not None
        
        
        # default rendering options
        if self.primitive_type is None:
            self.primitive_type = PrimitiveType.LineStrip
        if self.bounds is None:
            self.bounds = [0, self.size]
        self.bounds = np.array(self.bounds, dtype=np.int32)
        
        # if not self.default_color:
            # self.default_color = (1., 1., 0., 1.)
            
        
        if not self.attributes:
            self.add_attribute("position", vartype="float", ndim=2, location=0)
        
        if not self.fs_mains:
            self.add_fragment_main("""
            out_color = %s;
            """ % _get_shader_vector(self.default_color))
    
        
    
        # get the list of all template variable names
        vs = ["attributes", "uniforms", "textures", "compounds"]
        self.variable_names = list(itertools.chain(*[getattr(self, v) \
            for v in vs]))
        
        
        