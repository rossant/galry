Notes about the high-level API
==============================

This document contains some examples of how the future high-level API
can be used for specific tasks. The objectives of this API are:

  * simplicity
  * flexibility
  * object-oriented

It is inspired from the current Galry API as well as pyglet.


A yellow disc following the mouse
---------------------------------

    from galry import *

    f = figure()
    d = disc(color='y')

    @f.event
    def on_mouse_move(position, button, modifiers):
        d.position = position

    f.show()

In this example, the on_mouse_move function is called as soon as the mouse
moves. The position of the disc is then changed.

The following event is automatically created:

    @f.event
    def on_draw():
        f.clear()
        d.draw()
        
By default, the on_draw event clears the figure, and draws all objects defined
in the current namespace.


A simple plot
-------------

    from galry import *
    from numpy import *

    x = linspace(-10, 10, 1000)
    plot(x, sin(x))
    show()

Here, the plot function automatically activates the plotting interface,
which is a particular kind of figure, with interactive navigation (pan/zoom),
axes, grid, interactive tools (tooltip), etc.

Also, a figure is automatically created.


Mandelbrot fractal
------------------

    from galry import *
    from numpy import *
    
    f = figure()
    
    # add the possibility to navigate interactively
    f.features.navigation = True

    # constrain the figure to the default viewport
    f.viewport_max = f.viewport

    # create an empty image filling the whole window
    img = image(corners=f.viewport)
    
    # add a GLSL routine in the fragment shader which computes the color of 
    # a pixel in the fractal
    img.fragment_shader.routines += """
    float mandelbrot(float z0) {
        // ...
        return r;
    }
    """
    
    # change the 'color_out' variable in the fragment shader
    img.fragment_shader.color_out = """
        // ... z as a function of coords
        color_out = mandelbrot(z);
    """
    
    show()
    
In this example, the Mandelbrot fractal is shown in the window, and one can
navigate interactively within it.

There are several figure types (child classes deriving from Figure).
Figure2D, Figure3D (camera, etc.), Plot2D (with interactive navigation), 
Plot3D, etc.

f.features contains a list of boolean variables that allow to activate/deactive
certain features in the window. This list is specified by the specific Figure
class.
Examples for Plot2D:

  * navigation: pan/zoom
  * depth
  * antialiasing
  * fps
  * grid
  * axes
  * ratio

f.viewport contains the (x0, y0, x1, y1) coordinates of the current view.
By default: (-1, -1, 1, 1). f.viewport_max and f.viewport_min contain the
max and min viewports.

Each visual object has vertex_shader and fragment_shader attributes.
They have several sub-attributes that are used to modify the shaders.

    shader.main = """full main function"""
    shader.NAME = VALUE # replace template NAME by VALUE
    shader.routines = list of routines


TODO
----

Coordinate system transformation?
How to implement grid with this API?
How to implement Dynamic undersampling with external thread and HDF5?
Subplots?






