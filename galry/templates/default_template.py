from datatemplate import DataTemplate

class DefaultTemplate(DataTemplate):
    def add_transformation(self, is_static=False):
        """Add static or dynamic position transformation."""
        # dynamic navigation
        if not is_static:
            self.add_uniform("scale", vartype="float", ndim=2)
            self.add_uniform("translation", vartype="float", ndim=2)
            
            self.add_vertex_header("""
// Transform a position according to a given scaling and translation.
vec2 transform_position(vec2 position, vec2 scale, vec2 translation)
{
return scale * (position + translation);
}
            """)
            
            self.add_vertex_main("""
    gl_Position = vec4(transform_position(position, scale, translation), 
                   0., 1.);""")
        # static
        else:
            self.add_vertex_main("""
    gl_Position = vec4(position, 0., 1.);""")
        
    def add_constrain_ratio(self, constrain_ratio=False):
        if constrain_ratio:
            self.add_uniform("viewport", vartype="float", ndim=2)
            self.add_vertex_main("gl_Position.xy = gl_Position.xy / viewport;")
        
    def initialize(self, is_static=False, constrain_ratio=False):        
        self.is_static = is_static
        self.constrain_ratio = constrain_ratio
        
        self.add_transformation(is_static)
        self.add_constrain_ratio(constrain_ratio)
            
        