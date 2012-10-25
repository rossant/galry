import numpy as np

# Vertex shader template
# ----------------------
VS_TEMPLATE = """
// Attribute declarations.
%ATTRIBUTE_DECLARATIONS%

// Uniform declarations.
%UNIFORM_DECLARATIONS%

// Varying declarations.
%VARYING_DECLARATIONS%

// Transform a position according to a given scaling and translation.
vec4 transform_position(vec4 position, vec2 scale, vec2 translation)
{
    vec2 transformed_position = scale * (position.xy + translation);
    return vec4(transformed_position.xy, 0.0, 1.0);
}

// Core functions (including main()).
// By default, there is at least one attribute of vec4: `position`.
// gl_Position must be set as output, all other gl_* variables are deprecated.
%CORE%

"""

# Fragment shader template
# ------------------------
FS_TEMPLATE = """
// Uniform declarations.
%UNIFORM_DECLARATIONS%

// Varying declarations.
%VARYING_DECLARATIONS%

// Output color.
%FRAGMENT_OUTPUT%

// Core functions (including main()).
// gl_FragCoord is available, all other gl_* variables are deprecated.
%CORE%

"""

# Default vertex shader cores
# ---------------------------
STATIC_VS_CORE = """

void main()
{
    gl_Position = position;
}

"""

DYNAMIC_VS_CORE = """

void main()
{
    gl_Position = transform_position(position, scale, translation);
}

"""

# Default fragment shader core
# --------------------------
DEFAULT_FS_CORE = """

void main()
{
    out_color = vec4(1., 1., 1., 1.);
}

"""



class ShadersCreator(object):
    """Abstraction class for shaders source codes.
    
    The idea is that the developer provides the source code of the core 
    functions in the vertex and fragment shaders (i.e. `main()`). The different
    buffers, input variables, and vertex-to-fragment variables are declared
    in Python, and the corresponding code is automatically generated. This is
    to avoid compatibility issues with the different versions of OpenGL (and
    also OpenGL ES) that implement these declarations differently. For example,
    to pass a variable from the vertex to the fragment shader, one used to use
    `varying` in older versions of OpenGL, which is now deprecated and replaced
    by `in/out`. But in OpenGL ES, `in` and `out` keywords are not defined,
    one should rather use... `varying`.
    
    """
    # version = "330"
    
    # each item is a dict with the following keys:
    #   * name: variable name, as used in shaders code
    #   * vartype: 'bool', 'float' or 'int'
    #   * ndim: 1 (scalar), 2 ((i)vec2), 3 or 4
    #   * size: 1 (one value) or n (array)

    def __init__(self, is_static=False):
        self.attributes = []
        self.uniforms = []
        self.varyings = []
    
        self.fragment_core = DEFAULT_FS_CORE
        self.add_attribute("position", np.zeros((1, 4), dtype=np.float32))
        if is_static:
            self.vertex_core = STATIC_VS_CORE
        else:
            self.vertex_core = DYNAMIC_VS_CORE
            self.add_uniform("scale", (1., 1.))
            self.add_uniform("translation", (0., 0.))
            
    def _get_vartype(self, valuetype):
        if (valuetype == float) | (valuetype == np.float32):
            vartype = 'float'
        elif (valuetype == int) | (valuetype == np.int32):
            vartype = 'int'
        elif valuetype == bool:
            vartype = 'bool'
        return vartype
      
    def _get_value_info(self, value):
        """Give information about an uniform value type."""
        # array
        if isinstance(value, np.ndarray):
            vartype = self._get_vartype(value.dtype)
            if value.ndim == 1:
                size, ndim = value.size, 1
            elif value.ndim >= 2:
                size, ndim = value.shape
        # tuple
        elif type(value) is tuple:
            vartype = self._get_vartype(type(value[0]))
            ndim = len(value)
            size = None
        # scalar value
        else:
            vartype = self._get_vartype(type(value))
            ndim = 1
            size = None
        return dict(vartype=vartype, ndim=ndim, size=size)

    def _get_shader_type(self, value_info):
        if value_info["ndim"] == 1:
            shader_type = value_info["vartype"]
        else:
            shader_type = "vec%d" % value_info["ndim"]
            if value_info["vartype"] != "float":
                shader_type = "i" + shader_type
        return shader_type
    
    
    def add_attribute(self, name, value, location=None):
        dic = self._get_value_info(value)
        if location is None:
            location = len(self.attributes)
        self.attributes.append(dict(
            name=name,
            location=location,
            **dic
        ))
    
    def add_uniform(self, name, value):
        dic = self._get_value_info(value)
        self.uniforms.append(dict(
            name=name,
            **dic
        ))
        
    def add_varying(self, name, value):
        dic = self._get_value_info(value)
        self.varyings.append(dict(
            name=name,
            **dic
        ))
    
    
    
    
    def get_attribute_declarations(self):
        declarations = ""
        for attribute in self.attributes:
            declarations += "layout(location = %d) in %s %s;\n" % \
                (attribute["location"],
                 self._get_shader_type(attribute), 
                 attribute["name"])
        return declarations
        
    def get_uniform_declarations(self):
        declarations = ""
        for uniform in self.uniforms:
            tab = ""
            if uniform["size"] is not None:
                tab = "[%d]" % uniform["size"]
            # add uniform declaration
            declarations += "uniform %s %s%s;\n" % \
                (self._get_shader_type(uniform),
                 uniform["name"],
                 tab)
        return declarations
        
    def get_varying_declarations(self):
        vs_declarations = ""
        fs_declarations = ""
        for varying in self.varyings:
            s = "%%s %s %s;\n" % \
                (self._get_shader_type(varying), 
                 varying["name"])
            vs_declarations += s % "out"
            fs_declarations += s % "in"
        return vs_declarations, fs_declarations
    
    
    
        
    def get_vertex_core(self):
        return self.vertex_core
        
    def get_fragment_core(self):
        return self.fragment_core
    
    
    
    
    
    def set_vertex_core(self, core):
        self.vertex_core = core
    
    def set_fragment_core(self, core):
        self.fragment_core = core
    
    def get_shaders(self):
        vs_varying_declarations, fs_varying_declarations = \
                                            self.get_varying_declarations()
        vs = VS_TEMPLATE
        vs = vs.replace('%ATTRIBUTE_DECLARATIONS%', self.get_attribute_declarations())
        vs = vs.replace('%UNIFORM_DECLARATIONS%', self.get_uniform_declarations())
        vs = vs.replace('%VARYING_DECLARATIONS%', vs_varying_declarations)
        vs = vs.replace('%CORE%', self.get_vertex_core())
        
        fs = FS_TEMPLATE
        fs = fs.replace('%UNIFORM_DECLARATIONS%', self.get_uniform_declarations())
        fs = fs.replace('%VARYING_DECLARATIONS%', fs_varying_declarations)
        fs = fs.replace('%FRAGMENT_OUTPUT%', "out vec4 out_color;")
        
        fs = fs.replace('%CORE%', self.get_fragment_core())
        
        return vs, fs

    def __repr__(self):
        vs, fs = self.get_shaders()
        return vs + "\n\n\n\n" + fs
        
        
        
        
        

# # Textured rectangle
# # ------------------
    # textured_rectangle = {
        # "vertex": """
# %AUTODECLARATIONS%

# void main()
# {
    # if (!is_static)
        # gl_Position = gl_ModelViewProjectionMatrix * position;
    # else
        # gl_Position = position;
    # gl_FrontColor = gl_Color;
    
    # gl_TexCoord[0] = texture_coordinates;
# }
        # """,
        
        # "fragment": """
# uniform sampler2D tex_sampler0;

# void main()
# {
    # gl_FragColor = texture2D(tex_sampler0, gl_TexCoord[0].st);
# }
        # """
    # },
    
# # Sprites
# # -------
    # sprites={
    # "vertex": """
# %AUTODECLARATIONS%

# void main()
# {
    # if (!is_static)
        # gl_Position = gl_ModelViewProjectionMatrix * position;
    # else
        # gl_Position = position;
    # gl_FrontColor = gl_Color;
    
    # gl_PointSize = point_size;
# }
# """,

    # "fragment": """
# uniform sampler2D tex_sampler0;

# void main()
# {
    # gl_FragColor = texture2D(tex_sampler0, gl_PointCoord) * gl_Color;
# }
# """},

# # Colored sprites
# # ---------------
    # sprites_color={
    # "vertex": """
# %AUTODECLARATIONS%

# void main()
# {
    # if (!is_static)
        # gl_Position = gl_ModelViewProjectionMatrix * position;
    # else
        # gl_Position = position;
    # gl_FrontColor = color;
    
    # gl_PointSize = point_size;
# }
# """,

    # "fragment": """
# uniform sampler2D tex_sampler0;

# void main()
# {
    # gl_FragColor = texture2D(tex_sampler0, gl_PointCoord) * gl_Color;
# }
# """},
# )


if __name__ == '__main__':
    s = Shader()
    s.add_uniform("t", 0.0)
    s.add_attribute("color", (1.,1.,1.,1.))
    s.add_varying("out_pos", (0.,) * 3)
    print s