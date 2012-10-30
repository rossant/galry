import itertools
import collections
import sys
from ..debugtools import log_info, info_level

# HACK: Linux in VirtualBox uses OpenGL ES, which requires a special API
# in GLSL. This variable is true when OpenGL ES version 120 is used
# info_level()
OLDGLSL = sys.platform != "win32"
# log_info("OLDGLSL=%s" % str(OLDGLSL))





if not OLDGLSL:
    VS_TEMPLATE = """
#version 330
%VERTEX_HEADER%
void main()
{
    %VERTEX_MAIN%
}

"""

    FS_TEMPLATE = """
#version 330
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
%VERTEX_HEADER%
void main()
{
    %VERTEX_MAIN%
}

"""

    FS_TEMPLATE = """
#version 120
%FRAGMENT_HEADER%
void main()
{
    vec4 out_color = vec4(1., 1., 1., 1.);
    %FRAGMENT_MAIN%
    gl_FragColor = out_color;
}

"""
    

    
    
    
if not OLDGLSL:
    def _get_shader_type(varinfo):
        if varinfo["ndim"] == 1:
            shader_type = varinfo["vartype"]
        elif varinfo["ndim"] >= 2:
            shader_type = "vec%d" % varinfo["ndim"]
            if varinfo["vartype"] != "float":
                shader_type = "i" + shader_type
        return shader_type
else:
    def _get_shader_type(varinfo):
        if varinfo["ndim"] == 1:
            shader_type = "float" #varinfo["vartype"]
        elif varinfo["ndim"] >= 2:
            shader_type = "vec%d" % varinfo["ndim"]
            # if varinfo["vartype"] != "float":
                # shader_type = "i" + shader_type
        return shader_type
    
    
def _get_shader_vector(vec):
    return "vec%d%s" % (len(vec), str(vec))
    
    
    
    
    

def get_attribute_declaration(attribute):
    if not OLDGLSL:
        declaration = "layout(location = %d) in %s %s;\n" % \
                        (attribute["location"],
                         _get_shader_type(attribute), 
                         attribute["name"])
    else:
        declaration = "attribute %s %s;\n" % \
                        (_get_shader_type(attribute), 
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
    s = "%%s %s %s;\n" % \
        (_get_shader_type(varying), 
         varying["name"])
         
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
    def __init__(self, size=None):
        self.attributes = collections.OrderedDict()
        self.uniforms = {}
        self.textures = {}
        self.varyings = {}
        self.compounds = {}
        
        self.vs_headers = []
        self.vs_mains = []
        
        self.fs_headers = []
        self.fs_mains = []
        
        self.default_data = {}
        
        self.size = size
        
        # self.primitive_type = None
        self.bounds = None#[0, size]
        self.default_color = (1., 1., 0., 1.)
    
    def set_size(self, size):
        self.size = size
    
    # def set_default_data(self, name, data):
        # self.default_data[name] = data
    
    def add_attribute(self, name, location=None, default=None, **varinfo):
        if location is None:
            location = len(self.attributes)
        self.attributes[name] = dict(name=name, location=location, **varinfo)
        if default is not None:
            self.set_default_data(**{name:default})
        
    def add_uniform(self, name, default=None, **varinfo):
        self.uniforms[name] = dict(name=name, **varinfo)
        if default is not None:
            self.set_default_data(**{name:default})
        
    def add_varying(self, name, default=None, **varinfo):
        self.varyings[name] = dict(name=name, **varinfo)
        if default is not None:
            self.set_default_data(**{name:default})
        
    def add_texture(self, name, default=None, #location=None,
        **texinfo):
        # if location is None:
            # location = len(self.textures)
        self.textures[name] = dict(name=name, #location=location,
            **texinfo)
        if default is not None:
            self.set_default_data(**{name:default})
    
    def add_compound(self, name, **varinfo):
        self.compounds[name] = dict(name=name, **varinfo)
    
    def add_vertex_header(self, code):
        self.vs_headers.append(code)
        
    def add_vertex_main(self, code):
        self.vs_mains.append(code)
        
    def add_fragment_header(self, code):
        self.fs_headers.append(code)
        
    def add_fragment_main(self, code):
        self.fs_mains.append(code)
    
    def set_default_color(self, default_color=None): 
        if default_color is not None:
            self.default_color = default_color
    
    def set_rendering_options(self, primitive_type=None, bounds=None): 
        if primitive_type is not None:
            self.primitive_type = primitive_type
        if bounds is not None:
            self.bounds = bounds
    
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
        
        vs = vs.replace(b"\r\n", b"\n")
        fs = fs.replace(b"\r\n", b"\n")
        
        return vs, fs
    
    def set_default_data(self, **kwargs):
        """Set default data for template variables."""
        for name, data in kwargs.iteritems():
            self.default_data[name] = data
    
    def initialize(self, **kwargs):
        """Initialize the template by making calls to self.add_*.
        
        To be overriden.
        
        """
    
    def finalize(self):
        """Finalize the template to make sure that shaders are compilable.
        
        This is the place to implement any post-processing algorithm on the
        shader sources, like custom template replacements at runtime.
        
        """
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
        
        
        