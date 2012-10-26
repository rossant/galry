"""Tutorial 07: Introduction to shaders.

Things start to become serious in this tutorial.
It shows how to use vertex and fragment shaders. The data
passed to the GPU contains a flat function, that is transformed into
a sinus function (with a parametrizable frequency) by the vertex shader.

"""

# We import galry.
from galry import *
import numpy as np

# We first define a custom vertex shader. This small program, written in a
# C-like low-level language called GLSL, is compiled and runs on the GPU.
# At every frame, this program is executed in parallel for every single point.
# Here, it takes the initial position as input, and returns the final position.
# It also passes the default color to the fragment shader.
vertex_shader = """
// Main program.
void main()
{
    /* We overwrite the y coordinate as a function of the x coordinate of the
     * initial vector.
     */
    position.y = sin(frequency * position.x);
    
    /* `gl_Position` is the output of the shader: the final position in the 
     * world coordinate system. The `gl_ModelViewProjectionMatrix` is the
     * matrix containing the whole transformation from the world coordinate
     * system to the view coordinate system. In particular, it encodes 
     * panning and zooming.
     */
    gl_Position = gl_ModelViewProjectionMatrix * position;
    
    /* Here, we pass the default color specified with the `color` attribute
     * in `create_dataset` (or yellow by default) to the fragment shader.
     * Without this line, the fragment shader has no way to know the color,
     * so everything would be black.
     *
     * `gl_Color` contains this default color, `gl_FrontColor` corresponds to 
     * the `gl_Color` variable in the fragment shader.
     */
    gl_FrontColor = gl_Color;
}
"""

# We define the fragment shader, which is called for every primitive pixel.
# It takes as input `gl_Color` (corresponding to gl_FrontColor in the vertex
# shader) and returns the final color in `gl_FragColor`.
fragment_shader = """
// Main program.
void main()
{
    /* We simply assign the final pixel color to the color passed by the vertex
     * shader.
     */
    gl_FragColor = gl_Color;
}
"""

class MyPaintManager(PaintManager):
    def initialize(self):
        
        # Number of points.
        n = 10000
        
        # We create a dataset of size n.
        # This dataset will be used to eventually render n points as a 
        # LineStrip (n-1 successive line segments).
        # We also specify a white color, and our custom shaders.
        self.create_dataset(n,
                                 primitive_type=PrimitiveType.LineStrip,
                                 # Try commenting the following two lines
                                 # vertex_shader=vertex_shader,
                                 # fragment_shader=fragment_shader,
                                 # We define the frequency uniform with its
                                 # initial value.
                                 frequency = 20.,
                                 )
                                 
        # Initial positions of the points: on an horizontal line.
        positions = np.zeros((n, 2))
        positions[:,0] = np.linspace(-1., 1., n)
        
        # We add the positions to a data buffer named `position`. This is
        # the same name as used in the vertex shader.
        self.add_buffer("position", positions)

        self.set_shaders(vertex_shader=vertex_shader,
                         fragment_shader=fragment_shader,)
        
show_basic_window(paint_manager=MyPaintManager)
