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

class MyTemplate(DefaultTemplate):
    def get_initialize_arguments(self, **data):
        pos = data.get("initial_position", None)
        self.size = pos.shape[0]
        return {}
        
        
    def initialize(self, **kwargs):
        self.add_attribute("initial_position", vartype="float", ndim=2)
        
        self.add_uniform("frequency", vartype="float", ndim=1)
        
        self.add_vertex_main("""
    float x = initial_position.x;
    vec2 position = vec2(x, sin(frequency * x));
        """)
        
        super(MyTemplate, self).initialize(**kwargs)

class MyPaintManager(PaintManager):
    def initialize(self):
        
        # Number of points.
        n = 10000
        
        # Initial positions of the points: on an horizontal line.
        positions = np.zeros((n, 2))
        positions[:,0] = np.linspace(-1., 1., n)
        
        # We create a dataset of size n.
        # We also specify a white color, and our custom shaders.
        self.create_dataset(MyTemplate,
            initial_position=positions,
            # We set the frequency.
            frequency=20.)
        
show_basic_window(paint_manager=MyPaintManager)
