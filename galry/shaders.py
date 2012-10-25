












class Shader(object):
    
    version = "330"
    
    buffers = []
    uniforms = []
    
    def add_buffer(self, name, vartype, location=None):
        pass
    
    def add_uniform(self, name, vartype, location=None):
        pass
    
    def __repr__(self):
        return


        
        
        
# def _get_value_type(value):
    # """Give information about an uniform value type."""
    # # array
    # if isinstance(value, np.ndarray):
        # is_float = value.dtype == np.float32
        # is_bool= value.dtype == np.bool
        # size, ndim = value.shape
    # # tuple
    # elif type(value) is tuple:
        # is_float = (type(value[0]) == float) | (type(value[0]) == np.float32)
        # is_bool = type(value[0]) == bool
        # ndim = len(value)
        # size = None
    # # scalar value
    # else:
        # is_float = type(value) == float
        # is_bool = type(value) == bool
        # ndim = 1
        # size = None
    # return dict(is_float=is_float, is_bool=is_bool, ndim=ndim, size=size)

# # global counter for the buffer attribute location, allows to avoid 
# # specifying explicitely an unique location for each buffer
# SHADER_ATTRIBUTE_LOCATION = 0
# def get_new_attribute_location():
    # global SHADER_ATTRIBUTE_LOCATION
    # loc = SHADER_ATTRIBUTE_LOCATION
    # SHADER_ATTRIBUTE_LOCATION += 1
    # return loc
    
# def reset_attribute_location():
    # """Set the counter to 0 at initialization."""
    # global SHADER_ATTRIBUTE_LOCATION
    # SHADER_ATTRIBUTE_LOCATION = 0

    






    
        
        
     
# def process_vertex_shader_source(self, dataset):
    # """Process templated vertex shader source.
    
    # This method replaces %AUTODECLARATIONS% with the actual shader variable
    # declarations, based on what the dataset contains.
    
    # Arguments:
      # * dataset: the dataset.
      
    # Returns:
      # * dataset: the dataset with the updated shader code.
    
    # """
    
    # vs = dataset["vertex_shader"]
    
    # # autodeclaration of buffers
    # declarations = "// Buffer declarations.\n"
    # for name, buffer in dataset["buffers"].iteritems():
        
        # location = buffer["attribute_location"]
        
        # # find type declaration
        # if buffer["ndim"] == 1:
            # if buffer["dtype"] == np.float32:
                # vartype = "float"
            # else:
                # vartype = "int"
        # else:
            # # vartype = "vec%d" % buffer["ndim"]
            # # HACK: we force 4 dimensions, since everything will work with
            # # that
            # vartype = "vec%d" % 4 #buffer["ndim"]
            # if buffer["dtype"] != np.float32:
                # vartype = "i" + vartype
                
        # # add buffer declaration
        # declarations += "layout(location = %d) in %s %s;\n" % \
                                            # (location, vartype, name)
    
    # # autodeclaration of uniforms
    # declarations += "\n// Uniform declarations.\n"
    
    # # is_static
    # declarations += "uniform bool is_static;\n"
    
    # # all uniforms
    # for name, uniform in dataset["uniforms"].iteritems():
        
        # # HACK: particular case for texture-related uniforms: they
        # # are used in the fragment shader instead
        # if "tex_sampler" in name:
            # continue
            
        # typeinfo = _get_value_type(uniform["value"])
        
        # # handle array
        # tab = ""
        # if typeinfo["size"] is not None:
            # tab = "[%d]" % typeinfo["size"]
            
        # # find type declaration
        # if typeinfo["ndim"] == 1:
            # if typeinfo["is_float"]:
                # vartype = "float"
            # elif typeinfo["is_bool"]:
                # vartype = "bool"
            # else:
                # vartype = "int"
        # else:
            # vartype = "vec%d" % typeinfo["ndim"]
            # if not typeinfo["is_float"]:
                # vartype = "i" + vartype
                
        # # add uniform declaration
        # declarations += "uniform %s %s%s;\n" % (vartype, name, tab)
        
    # declarations += "\n"
        
    # # put auto declarations
    # vs = vs.replace("%AUTODECLARATIONS%", declarations)
    
    # # add version
    # vs = "#version 330\n" + vs
    
    # # save the modifications
    # dataset["vertex_shader"] = vs
         
        
        
        
        
        
        
# # default shaders
# DEFAULT_SHADERS = dict(
# # Position-only
# # -------------
    # position={
        # "vertex": """
# %AUTODECLARATIONS%

# void main()
# {
    # if (!is_static)
        # gl_Position = gl_ModelViewProjectionMatrix * position;
    # else
        # gl_Position = position;
    # gl_FrontColor = gl_Color;
# }
        # """,
        
        # "fragment": """
# void main()
# {
    # gl_FragColor = gl_Color;
# }
        # """
    # },
    
# # Position and color
# # ------------------
    # position_color={
        # "vertex": """
# %AUTODECLARATIONS%

# void main()
# {
    # if (!is_static)
        # gl_Position = gl_ModelViewProjectionMatrix * position;
    # else
        # gl_Position = position; 
    # gl_FrontColor = color;
# }
        # """,
        
        # "fragment": """
# void main()
# {
    # gl_FragColor = gl_Color;
# }
        # """
    # },

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
