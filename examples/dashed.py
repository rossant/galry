"""Dashed plot example.

A custom fragment shader is written in order to allow for dashed plots.

"""
from galry import *
import numpy as np

# We define a new Template, which consists in a set of variables and
# shader code written in GLSL. The code describes how the data contained in
# the different variables is rendered as pixels.
class DashedPlotTemplate(DefaultTemplate):
    
    # The main method to override is initialize, which contains the definitions
    # of the different variables, along with the shader codes.
    # Note: the keyword arguments is mandatory, so that the parent templates
    # can handle navigation-related variables.
    def initialize(self, **kwargs):
       
       # We define an attribute: an array variable with n scalars or vectors.
       # The most common attribute is the position, which contains the
       # coordinate of a point. There is one execution of the shader kernel
       # per point.
       # In addition to the name, several properties of this variable must
       # be given: vartype (a string: 'float', 'int' or 'bool'), ndim 
       # (1 for a scalar, 2, 3 or 4 for a vector). The name of an attribute
       # is used in the vertex shader and the corresponding varialbe contains
       # one element of the array (so a scalar or a 2/3/4-vector).
       self.add_attribute("position", vartype='float', ndim=2)
       
       # An uniform is a global variable, that can be used in both vertex and 
       # fragment shaders, and which is the same for all points. Here it is
       # the color of the point. We directly give its default value (which
       # can be changed during the execution of the widget) so we don't 
       # necessarily need to specify the variable properties (vartype, ndim...)
       self.add_uniform("color", data=(1., 1., 0., 1.))
       
       # We arrive to the part specific to this example. In order to implement
       # dashed plots, we define a variable that will be ultimately used
       # in the fragment shader, so by each pixel of the curve. This variable
       # contains a value between 0 and 1 according to the position in the
       # whole curve (0 = leftmost pixel, 1 = rightmost pixel). From this
       # variable, we'll be able to calculate the opacity of that pixel (which
       # will be either 0 or 1).
       # The fragment shader cannot have access to attributes. However, they
       # can have access to variables passed by the vertex shader: these
       # are call varying variables. So we define first an attribute, then
       # a varying which will be set by the vertex shader.
       coords = np.linspace(0., 1., self.size)
       self.add_attribute("coord_vs", data=coords)
       self.add_varying("coord", vartype='float', ndim=1)
       
       # This GLSL code transfers the attribute value to the varying variable.
       self.add_vertex_main("""coord = coord_vs;""")
       
       # Now, in the fragment shader, we have access to the `coord` variable.
       # Since a fragment shader is executed on a per-pixel basis, whereas
       # a vertex shader is executed on a per-vertex basic, the value of 
       # the varying is interpolated here.
       self.add_fragment_main("""
    // coord is in [0, 1], and a regularly alternates between 0 and 1.
    float a = floor(mod(coord * 500, 2));
    
    // in the fragment shader, the color of the pixel must be defined in
    // out_color, which is a vec4. color is the uniform, and the mathematical
    // operations on vectors can be used naturally here.
    out_color = color;
    out_color.a *= a;
       """)
       
       # We need this for interactive navigation, which is implemented
       # in the parent class DefaultTemplate.
       self.initialize_default(**kwargs)

class MyPaintManager(PaintManager):
    def initialize(self):
        
        # We define the plot here.
        n = 1000
        x = np.linspace(-1., 1., n)
        position = np.zeros((n, 2))
        position[:,0] = x
        position[:,1] = .2 * np.sin(20 * x)
        
        # We create a dataset following our custom template, and pass
        # the `position` data (the name of the attribute variable).
        # We could also specify the color value, or any attribute/uniform/
        # texture variable defined in the template.
        self.create_dataset(DashedPlotTemplate, position=position)
        
        # We can add as many datasets as we want in the paint manager,
        # but the performance will decrease with the number of datasets.
        # Homogeneous data should be grouped as much as possible into 
        # one or a very small number of datasets.
        position = position.copy()
        position[:,1] = .2 * np.cos(20 * x)
        self.create_dataset(DashedPlotTemplate, position=position,
            color=(1., 0., 0., 1.))

show_basic_window(paint_manager=MyPaintManager)
