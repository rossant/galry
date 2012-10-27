
VS_TEMPLATE = """
%VERTEX_HEADER%

void main()
{
    %VERTEX_MAIN%
}

"""


FS_TEMPLATE = """
%FRAGMENT_HEADER%

out vec4 out_color;

void main()
{
    %FRAGMENT_MAIN%
}
"""


def _get_shader_type(varinfo):
    if varinfo["ndim"] == 1:
        shader_type = varinfo["vartype"]
    elif varinfo["ndim"] >= 2:
        shader_type = "vec%d" % varinfo["ndim"]
        if varinfo["vartype"] != "float":
            shader_type = "i" + shader_type
    return shader_type

def _get_shader_vector(vec):
    return "vec%d%s" % (len(vec), str(vec))
    
    
    
    
    

def get_attribute_declaration(attribute):
    declaration = "layout(location = %d) in %s %s;\n" % \
                    (attribute["location"],
                     _get_shader_type(attribute), 
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
    vs_declaration = s % "out"
    fs_declaration = s % "in"
    return vs_declaration, fs_declaration






class DataTemplate(object):
    def __init__(self, size):
        self.attributes = {}
        self.uniforms = {}
        self.textures = {}
        self.varyings = {}
        
        self.vs_headers = []
        self.vs_mains = []
        
        self.fs_headers = []
        self.fs_mains = []
        
        self.default_data = {}
        
        self.size = size
        
        # self.primitive_type = None
        # self.bounds = None
        self.default_color = (1.,) * 4
    
    def set_default_data(self, name, data):
        self.default_data[name] = data
    
    def add_attribute(self, name, location=None, **varinfo):
        if location is None:
            location = len(self.attributes)
        # print name, varinfo
        self.attributes[name] = dict(name=name, location=location, **varinfo)
        
    def add_uniform(self, name, **varinfo):
        self.uniforms[name] = dict(name=name, **varinfo)
        
    def add_varying(self, name, **varinfo):
        self.varyings[name] = dict(name=name, **varinfo)
        
    def add_texture(self, name, location=None, **texinfo):
        if location is None:
            location = len(self.textures)
        self.textures[name] = dict(name=name, **texinfo)
    
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
        
        return vs, fs
    
    def initialize(self):
        """Initialize the template by making calls to self.add_*.
        
        To be overriden.
        
        """
        pass
    
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
    
  