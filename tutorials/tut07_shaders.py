"""Tutorial 07: Introduction to shaders.

Things start to become serious in this tutorial.
It shows how to use vertex and fragment shaders. The data
passed to the GPU contains a flat function, that is transformed into
a sinus function (with a parametrizable frequency) by the vertex shader.

"""

# We import galry.
from galry import *
import numpy as np


class MyVisual(Visual):
    def initialize(self, initial_position=None, frequency=None):
        
        self.size = initial_position.shape[0]
        
        self.add_attribute("initial_position", vartype="float", ndim=2,
            data=initial_position)
        
        self.add_uniform("frequency", vartype="float", ndim=1,
            data=frequency)
        
        # We define a custom vertex shader. This small program, written in a
        # C-like low-level language called GLSL, is compiled and runs on the GPU.
        # At every frame, this program is executed in parallel for every single point.
        # Here, it takes the initial position as input, and returns the final position.
        self.add_vertex_main("""
    float x = initial_position.x;
    vec2 position = vec2(x, sin(frequency * x));
        """)
        

class MyPaintManager(PaintManager):
    def initialize(self):
        
        # Number of points.
        n = 10000
        
        # Initial positions of the points: on an horizontal line.
        positions = np.zeros((n, 2))
        positions[:,0] = np.linspace(-1., 1., n)
        
        # We add our visual.
        self.add_visual(MyVisual,
                        initial_position=positions,
                        # We set the frequency.
                        frequency=20.)
        
show_basic_window(paint_manager=MyPaintManager)
