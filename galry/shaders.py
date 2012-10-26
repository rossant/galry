import numpy as np
from debugtools import log_debug

__all__ = ["ShadersCreator"]

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
vec2 transform_position(vec2 position, vec2 scale, vec2 translation)
{
    return scale * (position + translation);
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

// Texture sampler declarations.
%TEXTURE_DECLARATIONS%

// Varying declarations.
%VARYING_DECLARATIONS%

// Output color.
%FRAGMENT_OUTPUT%

// Core functions (including main()).
// gl_FragCoord is available, all other gl_* variables are deprecated.
%CORE%

"""

# Default vertex shader core
# --------------------------
DEFAULT_VS_CORE = """

void main()
{
    %GET_POSITION%
    // Take viewport into account.
    gl_Position.xy = gl_Position.xy / viewport;
    
    %GET_VARYING_COLOR%
    
    %GET_VARYING_COORDINATES%
    
    %GET_POINT_SIZE%
}

"""

# Default fragment shader core
# ----------------------------
DEFAULT_FS_CORE = """

void main()
{
    %GET_OUT_COLOR%
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

    # is_ready = False
    
    def __init__(self, is_static=False):
        self.attributes = {}
        self.uniforms = {}
        self.textures = {}
        self.varyings = {}
        self.is_static = is_static
    
        self.vertex_core = DEFAULT_VS_CORE
        self.fragment_core = DEFAULT_FS_CORE
        
        # varying color variable by default, set by the vertex shader
        self.add_varying("varying_color", (1., 1., 0., 1.))
        
    # Internal methods
    # ----------------
    def _get_vartype(self, valuetype):
        if (valuetype == float) | (valuetype == np.float32):
            vartype = 'float'
        elif (valuetype == int) | (valuetype == np.int32):
            vartype = 'int'
        elif valuetype == bool:
            vartype = 'bool'
        else:
            vartype = None
        return vartype
      
    def _get_value_info(self, value):
        """Give information about an uniform value type."""
        # array
        if isinstance(value, np.ndarray):
            vartype = self._get_vartype(value.dtype)
            if value.ndim == 1:
                size, ndim = value.size, 1
            elif value.ndim == 2:
                size, ndim = value.shape
            elif value.ndim == 3:
                w, h, ndim = value.shape
                size = w, h
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
        elif value_info["ndim"] >= 2:
            shader_type = "vec%d" % value_info["ndim"]
            if value_info["vartype"] != "float":
                shader_type = "i" + shader_type
        return shader_type
    
    # Public methods
    # --------------
    def add_attribute(self, name, value, location):
        dic = self._get_value_info(value)
        # if location is None:
            # location = len(self.attributes)
        self.attributes[name] = dict(name=name,
                                       location=location,
                                       **dic)
        # self.is_ready = True
        # return location
        if name == "color":
            self.ndim_color = dic["ndim"]
    
    def add_texture(self, name, value, location, is_sprite=False):
        dic = self._get_value_info(value)
        # if location is None:
            # location = len(self.attributes)
        self.textures[name] = dict(name=name,
                                   is_sprite=is_sprite,
                                   location=location,
                                   **dic)
        # add texture coordinates varying variable
        # self.add_attribute("tex_coords", (0., 0.))
        if not is_sprite:
            self.add_varying("varying_tex_coords", (0., 0.))
    
    def add_uniform(self, name, value):
        if "tex_sampler" in name:
            log_debug("discarding '%s' uniform because it is a \
                        texture sampler" % name)
            return
        dic = self._get_value_info(value)
        self.uniforms[name] = dict(name=name, **dic)
        # self.is_ready = True
        if name == "color":
            self.ndim_color = dic["ndim"]
        
    def add_varying(self, name, value):
        dic = self._get_value_info(value)
        self.varyings[name] = dict(name=name, **dic)
        # self.is_ready = True
    
    def set_vertex_core(self, core):
        self.vertex_core = core
    
    def set_fragment_core(self, core):
        self.fragment_core = core
    
    # Declaration methods
    # -------------------
    def get_attribute_declarations(self):
        declarations = ""
        for name, attribute in self.attributes.iteritems():
            declarations += "layout(location = %d) in %s %s;\n" % \
                (attribute["location"],
                 self._get_shader_type(attribute), 
                 attribute["name"])
        return declarations
        
    def get_uniform_declarations(self):
        declarations = ""
        for name, uniform in self.uniforms.iteritems():
            tab = ""
            if uniform["size"] is not None:
                tab = "[%d]" % uniform["size"]
            # add uniform declaration
            declarations += "uniform %s %s%s;\n" % \
                (self._get_shader_type(uniform),
                 uniform["name"],
                 tab)
        return declarations
        
    def get_texture_declarations(self):
        declarations = ""
        for name, texture in self.textures.iteritems():
            # add texture declaration
            declarations += "uniform sampler2D %s;\n" % (texture["name"])
        return declarations
        
    def get_varying_declarations(self):
        vs_declarations = ""
        fs_declarations = ""
        for name, varying in self.varyings.iteritems():
            s = "%%s %s %s;\n" % \
                (self._get_shader_type(varying), 
                 varying["name"])
            vs_declarations += s % "out"
            fs_declarations += s % "in"
        return vs_declarations, fs_declarations
    
    # Core methods
    # ------------
    def get_vertex_core(self):
        return self.vertex_core
        
    def get_fragment_core(self):
        return self.fragment_core
    
    # Shader methods
    # --------------
    def get_shaders(self):
        vs_varying_declarations, fs_varying_declarations = \
                                            self.get_varying_declarations()
                
        # Vertex shader
        # -------------                           
        vs = VS_TEMPLATE
        vs = vs.replace('%ATTRIBUTE_DECLARATIONS%', self.get_attribute_declarations())
        vs = vs.replace('%UNIFORM_DECLARATIONS%', self.get_uniform_declarations())
        vs = vs.replace('%VARYING_DECLARATIONS%', vs_varying_declarations)
        vs = vs.replace('%CORE%', self.get_vertex_core())
        
        if self.is_static:
            vs = vs.replace('%GET_POSITION%', 
                """gl_Position = vec4(position, 0., 1.);""")
        else:
            vs = vs.replace('%GET_POSITION%', 
                """gl_Position = vec4(transform_position(position, scale, translation), 
                        0., 1.);""")
        
        if self.ndim_color == 3:
            vs = vs.replace('%GET_VARYING_COLOR%', 
                """varying_color = vec4(color.xyz, 1.0);""")
        elif self.ndim_color == 4:
            vs = vs.replace('%GET_VARYING_COLOR%', 
                """varying_color = color;""")
        
        
        
        # Fragment shader
        # ---------------
        fs = FS_TEMPLATE
        fs = fs.replace('%UNIFORM_DECLARATIONS%', self.get_uniform_declarations())
        fs = fs.replace('%TEXTURE_DECLARATIONS%', self.get_texture_declarations())
        fs = fs.replace('%VARYING_DECLARATIONS%', fs_varying_declarations)
        fs = fs.replace('%FRAGMENT_OUTPUT%', "out vec4 out_color;")
        fs = fs.replace('%CORE%', self.get_fragment_core())
        
        # textures
        if self.textures and not self.textures.items()[0][1]["is_sprite"]:
            
            vs = vs.replace('%GET_VARYING_COORDINATES%', 
                    """varying_tex_coords = tex_coords;""")
                    
            vs = vs.replace('%GET_POINT_SIZE%', "")
            
            fs = fs.replace('%GET_OUT_COLOR%', 
"""out_color = texture(tex_sampler0, varying_tex_coords) * varying_color;""")

        # sprites
        elif self.textures and self.textures.items()[0][1]["is_sprite"]:
            
            vs = vs.replace('%GET_VARYING_COORDINATES%', "")
            vs = vs.replace('%GET_POINT_SIZE%', "gl_PointSize = point_size;")
            
            fs = fs.replace('%GET_OUT_COLOR%', 
"""out_color = texture(tex_sampler0, gl_PointCoord) * varying_color;""")


        else:
           
            vs = vs.replace('%GET_VARYING_COORDINATES%', "") 
            
            vs = vs.replace('%GET_POINT_SIZE%', "")
            
            fs = fs.replace('%GET_OUT_COLOR%', 
                    """out_color = varying_color;""")
        
        
    # gl_Position = vec4(transform_position(position, scale, translation), 
                        # 0., 1.);
    
    # varying_color = vec4(color);
        
        
        return vs, fs

    def __repr__(self):
        vs, fs = self.get_shaders()
        return vs + "\n\n\n\n" + fs
        
        
        
        
        

if __name__ == '__main__':
    s = ShadersCreator()
    s.add_uniform("t", 0.0)
    s.add_attribute("position", (1.,1.,1.,1.), 0)
    s.add_attribute("color", (1.,1.,1.), 1)
    s.add_texture("tex_sampler0", None, 0)
    s.add_attribute("tex_coords", (0., 0.), 2)
    s.add_varying("out_pos", (0.,) * 4)
    print s