from galry import *
import numpy as np

# Vertex shader
VS = """
// Use this template variable to auto-declare shader declarations.
%AUTODECLARATIONS%

void main()
{
    // Update coordinate y as a function of x.
    vec4 newpos = position;
    newpos.y = sin(10 * position.x);
    
    // Transform the position in order to take interactive navigation into
    // account.
    gl_Position = gl_ModelViewProjectionMatrix * newpos;
    
    // Pass the default color to the fragment shader.
    gl_FrontColor = gl_Color;
}
"""

# Fragment shader
FS = """
void main()
{
    // Use directly the color passed by the vertex shader.
    gl_FragColor = gl_Color;
}
"""

N = 1000
# generate points on an horizontal line
positions = np.zeros((N, 2))
positions[:,0] = np.linspace(-1., 1., N)

class ShaderPaintManager(PaintManager):
    def initialize(self):
        # create a dataset with a line strip
        ds = self.create_dataset(N,
                                 primitive_type=PrimitiveType.LineStrip,
                                 vertex_shader=VS,
                                 fragment_shader=FS)
        self.add_buffer("position", positions)
    
if __name__ == '__main__':
    window = show_basic_window(paint_manager=ShaderPaintManager)
    