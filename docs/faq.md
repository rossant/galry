FAQ
===

Why Galry?
----------

Most visualization packages in Python are either meant to generate high-quality
publication-ready figures (like matplotlib), or to offer 3D fast interactive 
visualization (like mayavi).
Existing 2D plotting packages do not generally offer an efficient way to 
interactively visualize large datasets (1, 10, even 100 million points). 
The main goal of Galry is to provide the most optimized way of visualizing
large 2D/3D datasets, by using the full power of the graphics card.


How fast is it?
---------------

Performance and speed are the major objectives of Galry. The Python overhead
is minimized so that performance is only limited by the power of the
graphics card. We can approximately assess the performance of Galry by
measuring the number of frames per second (FPS) when navigating in a scene
containing a large number of points.

Here are some results with a basic benchmark consisting of an N points plot
(`benchmarks/benchmark01_points.py`). 
*More systematic and automatic benchmark methods will be considered in the 
near future.*

On a 2012 desktop computer with a high-end AMD Radeon HD 7870 graphics card:

  * N = 10 million points: ~125 FPS
  * N = 20 million points: ~80 FPS
  * N = 50 million points: ~35 FPS
  * N = 100 million points: ~15 FPS

The [benchmark page](https://github.com/rossant/galry/wiki/Benchmarks) contains 
more details. Users are invited to do their own benchmark.


What can I do with Galry?
-------------------------

You can either:

  * Visualize large 2D/3D datasets consisting of points, lines, textures,
    meshes, and pan/zoom smoothly into your data.
    
  * Create your own customized GUI designed for highly efficient specialized
    interactive visualization of large 2D/3D datasets.
    
Galry is fully customizable, and you can either write a specialized scientific
visualization GUI, a particle system, a fractal viewer, or even a video
game (Pong can be written in 150 lines of commented code) !
All those examples are implemented in the `examples` folder.

### Custom visualization

The library gives you full control on the rendering pipeline process, through
the use of **vertex and fragment shaders**. Shaders are small programs written
in a simple C-like low-level language
([GLSL](http://en.wikipedia.org/wiki/GLSL)) 
that are dynamically compiled on the GPU.
They transform the raw data stored in GPU memory to pixels on the screen.
Learning and using GLSL lets you exploit the full power of the GPU for
the most optimized possible way of rendering data.

Helper functions are also included for common tasks such as displaying
lines, points, polygons, textures, point sprite textures, 3D meshes, and text.

### Custom interactivity

The library gives you full control on the interaction system.
*User actions* such as mouse clicks, mouse mouvements, keystrokes, etc., 
can be linked to arbitrary *interaction events* such as panning, zooming, etc.
You can define new interaction events and decide how exactly they interfere
with rendering. Possible uses include selection of objects, layout
modifications, etc.

### Integration in Qt

Galry provides a Qt widget written in Python displaying an OpenGL rendering
viewport. This widget contains your data. It can also interact with other
Qt widgets within a single application, in particular through the use of 
Qt signals and slots. These are the normal way Qt widgets talk to each other,
and they allow the development of a full visualization GUI with one or
several Galry widgets. The Galry interaction system can be easily linked
to the Qt interaction system based on signals and slots.

Integration with other GUI systems like TKinter or wx, might be considered
as some point. The only constraint is that this system provides an OpenGL
context.


How to get started?
-------------------

The [installation page](https://github.com/rossant/galry/wiki/Installation)
contains details on how to install Galry. Basically you first need to
install all dependencies (Python 2.7, Numpy, Matplotlib, PyOpenGL, PyQt4 or
PySide), then do `python setup.py install` in Galry's directory.

Documentation, examples and tutorials are available in Galry's package.

  * The manual gives a high-level overview of the library.
    
  * The tutorials provide a good way to start learning Galry.

  * The examples cover a wide range of Galry's possibilities.
    
    
How did this project start?
---------------------------

Galry is developed in the context of the creation of
a new electrophysiological data GUI that will handle very large datasets.
This GUI is still in development and should be released in 2013.
The development of Galry will be done in parallel.


What are the related packages?
------------------------------

Glumpy also contains some ideas to use OpenGL for interactive plotting in
Python. It might be integrated into Matplotlib at some point, as an OpenGL
backend.



