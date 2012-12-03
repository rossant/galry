Welcome to Galry: high performance interactive 2D visualization in Python
=========================================================================

**Important note: Galry is still in development. The programming interface
may change without notice.**

### Quick links

  * [Installation wiki](https://github.com/rossant/galry/wiki/Installation)
  * [Galry Users Google Group](https://groups.google.com/forum/?fromgroups#!forum/galry-users)
  * [Benchmarks wiki](https://github.com/rossant/galry/wiki/Benchmarks)
  * [User Manual](https://github.com/rossant/galry/blob/master/docs/manual.md)
  * [Tutorials](https://github.com/rossant/galry/tree/master/tutorials)
  * [Source code](https://github.com/rossant/galry)
  
  
What's new? [2012-12-02]
------------------------

  * The rendering engine has been entirely rewritten in order to increase
    the separation between the scene creation logic, and the actual GL 
    rendering.
  * This new architecture will make it easier to integrate Galry into the
    **IPython notebook**. A highly experimental proof of concept has been
    implemented and gives encouraging results (see the `experimental` folder).
  * A **high-level interface**, much similar to the pylab interface of
    matplotlib,
    will be available later. Using Galry for high-performance interactive 
    visualization with a given plotting script using matplotlib will just be
    a matter of replacing `import pylab as plt` with
    `import galry.plot as plt`.
  * It will be possible to automatically convert a Python plotting
    script using Galry to **WebGL/Javascript code** for integration within a
    standalone webpage. No Python required for running the webpage, just
    a WebGL-enabled browser.
  * The interaction system will be improved soon and the interface will
    probably change.
  * New features:
      * More efficient data updating system: before, the data could be changed
        at the condition that the size of all attributes and textures were kept
        unchanged. This limitation has fortunately disappeared.
      * Support for **texture filtering** options (including mipmapping).
      * Support for 1D and non-square textures.
      * Support for reference buffers: the same memory buffer on the GPU
        can now be used for several visuals in order to save memory
        (useful for graph rendering, where edges and nodes share the same
        memory buffer on the GPU).
      * Support for indexed rendering (index buffers). Useful for graph
        rendering where the edges are specified with indices targetting
        node positions.
      * New example: dynamic planar **graph rendering** with a simple CPU-based
        physics engine.
      * New example: **3D mesh** viewer (adapted from an example in Glumpy).
      * New example: **Pong video game**.
  * The 
    [context of the development of Galry can be found on this blog post](http://cyrille.rossant.net/galrys-story-or-the-quest-of-multi-million-plots/).


What is Galry?
--------------

Galry is a **high performance interactive visualization package in 
Python**. It lets you visualize and navigate into very large plots (signals,
points, textures...) in real time, by using the graphics card as much as
possible. Galry is written directly on top of PyOpenGL for the highest
performance possible.
OpenGL is a widely used hardware-accelerated open library implemented in
virtually every graphics card. As of today, it is probably the most efficient
portable low-level library for interactive rendering.

On a 2012 computer with a recent graphics card, one can interactively
visualize as much as **100 million points** at a reasonable framerate.
High performance is achieved through techniques coming from real-time 3D 
video games.

Galry is not meant to generate high-quality plots (like matplotlib), and is
more "low-level". It can be used to write complex interactive visualization
GUIs that deal with large 2D/3D datasets (only with QT for now). Galry is
fully customizable, and all aspects of rendering and interaction can be 
controlled by the developer.

Galry is based on PyOpenGL and Numpy and should work on any platform
(Window/Linux/MacOS).
Mandatory dependencies include Python 2.7, Numpy, either PyQt4 or PySide,
PyOpenGL, matplotlib.

Optional dependencies include IPython, PIL, hdf5, PyOpenCL (the last two are
not currently used but may be in the future).

Galry is licensed under the BSD license.


I want to see a demo!
---------------------

[![Galry's Demo](https://raw.github.com/rossant/galry/master/images/youtube.png)](http://www.youtube.com/watch?v=jYNJJ4O3pXo)


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

### Integration in QT

Galry provides a QT widget written in Python displaying an OpenGL rendering
viewport. This widget contains your data. It can also interact with other
QT widgets within a single application, in particular through the use of 
QT signals and slots. These are the normal way QT widgets talk to each other,
and they allow the development of a full visualization GUI with one or
several Galry widgets. The Galry interaction system can be easily linked
to the QT interaction system based on signals and slots.

Integration with other GUI systems like TKinter or wx, might be considered
as some point. The only constraint is that this system provides an OpenGL
context.


How to get started?
-------------------

At the time of writing, the code is still experimental and is not
guaranteed to work on any platform. The programming interface might change
without notice. Installation may be
difficult depending on the OS and the graphics card drivers (even if it has
been successfully tested on Windows, Linux and MacOS systems as of now).
That being said, please feel
free to download the library and take a look to the documentation.

The [installation page](https://github.com/rossant/galry/wiki/Installation)
also contains details on how to install Galry. 

There are several sources of documentation, all available in the `docs` folder.
Examples and tutorials are in separated folders.

  * The user guide: a high-level overview of the library. It's a good starting 
    point if you prefer a top-down approach.
    
  * The tutorials: hands-on tutorials to start galrying now. They're a good
    starting point if you prefer a bottom-up approach. They contain more 
    technical details than the user guide. It is recommanded that you go
    through both the user guide and the tutorials anyway.

  * The examples: they cover a wide range of Galry's possibilities.
    
  * The API reference: once you know the fundamentals, use the reference
    if you want to go deeper into Galry. It will be available on the wiki at
    some point, for now you'll have to look at the docstrings in the code...
    
    
How did this project start?
---------------------------

Galry is developed in the context of the creation of
a new electrophysiological data GUI that will handle very large datasets.
This GUI is still in development and should be released in 2013.
The development of Galry will be done in parallel.


I want to participate!
----------------------

[Send me an e-mail](http://cyrille.rossant.net).

