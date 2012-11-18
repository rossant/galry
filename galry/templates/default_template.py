from datatemplate import DataTemplate

class DefaultTemplate(DataTemplate):
    """Default data template that implements navigation."""
    
    position_attribute_name = "position"
    
    def add_transformation(self, is_static=False):
        """Add static or dynamic position transformation."""
        
        # dynamic navigation
        if not is_static:
            self.add_uniform("scale", vartype="float", ndim=2, data=(1., 1.))
            self.add_uniform("translation", vartype="float", ndim=2, data=(0., 0.))
            
            self.add_vertex_header("""
// Transform a position according to a given scaling and translation.
vec2 transform_position(vec2 position, vec2 scale, vec2 translation)
{
return scale * (position + translation);
}
            """)
            
            self.add_vertex_main("""
    gl_Position = vec4(transform_position(%s, scale, translation), 
                   0., 1.);""" % self.position_attribute_name)
        # static
        else:
            self.add_vertex_main("""
    gl_Position = vec4(%s, 0., 1.);""" % self.position_attribute_name)
        
    def add_constrain_ratio(self, constrain_ratio=False):
        """Add viewport-related code."""
        self.add_uniform("viewport", vartype="float", ndim=2, data=(1., 1.))
        self.add_uniform("window_size", vartype="float", ndim=2, data=(100., 100.))
        if constrain_ratio:
            self.add_vertex_main("gl_Position.xy = gl_Position.xy / viewport;")

    def get_initialize_arguments(self, **data):
        """Infer size from position attribute."""
        position = data.get("position", None)
        if position is not None:
            self.size = position.shape[0]
            
    def initialize_default(self, is_static=False, constrain_ratio=False, **kwargs): 
        """Default initialization with navigation-related code."""
        self.is_static = is_static
        self.constrain_ratio = constrain_ratio
        
        self.add_transformation(is_static)
        self.add_constrain_ratio(constrain_ratio)
        
    def initialize(self, **kwargs):
        self.initialize_default(**kwargs)
