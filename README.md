Welcome to Galry: a high performance interactive visualization package in Python
=================================================================================

**Important note: Galry is still in development. The programming interface
may change without notice.**

### Quick links

  * [What's new?](https://raw.github.com/rossant/galry/master/CHANGES.md)
  * [Installation wiki](https://github.com/rossant/galry/wiki/Installation)
  * [Galry Users Google Group](https://groups.google.com/forum/?fromgroups#!forum/galry-users)
  * [Benchmarks wiki](https://github.com/rossant/galry/wiki/Benchmarks)
  * [User Manual](https://github.com/rossant/galry/blob/master/docs/manual.md)
  * [Tutorials](https://github.com/rossant/galry/tree/master/tutorials)
  * [Source code](https://github.com/rossant/galry)
  
  
What's new? [2012-12-17]
------------------------

  * **High-level interface**: this new interface is a thin wrapper to the
    low-level interface. It provides a matplotlib-like interface which allows
    to easily add plots or any visuals on the scene, as well as defining
    custom handlers for events, and defining new events associated to 
    user actions.
  * All **tutorials** and **examples** have been updated to use this new
    high-level interface.
  * The **interaction system** has been refined and is now more modular.
    One can define standalone EventProcessors which register handlers
    for different events. Processors are then added in the InteractionManager.
    A given processor can be used separately in different managers and 
    widgets.
  * **New visuals**:
      * **GridVisual** (with grid, axes, ticks) but does not support
        automatic data normalization yet,
      * **BarVisual** (barplots, histograms) has been promoted from an example
        to a built-in, standalone visual,
      * **GraphVisual**, to plot graphs with colored nodes and edges (with
        reference buffer and indexed arrays for maximum memory efficiency),
      * **MeshVisual** to display a 3D mesh (along with a Python function to
        load a .OBJ ASCII object).
  * New Help option (H keyboard shortcut) to automatically display all bindings
    between user actions (mouse, keyboard, etc.) and events. It is quite
    convenient because it is dynamically and automatically generated
    as a function of the bindings in the current interaction mode.
  * Removed obsolete examples and restructured completely the tutorials.
    There will be three parts in the tutorials:
      * high-level interface for plotting and custom visuals,
      * high-level interface for custom interaction management,
      * low-level interface.
    Only the first half of the tutorials are done for now.
  * New tutorials/examples: raster plot with spikes as sprites, photo gallery:
    provide a folder with JPG images as argument and you can visualize all
    your photos in fullscreen.
  * Fixed segmentation fault on Linux with NVidia drivers which occurred
    when non-textured visuals where rendered before a textured visual.
  * Got rid of all enumerations, which added complexity and harmed readibility.
    It was not such a good idea to use them in the first place.
    Python ain't C#.
    
  
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

[![Galry's Demo](https://raw.github.com/rossant/galry/master/images/youtube.png)](http://www.youtube.com/watch?v=Nv4aNR4Gi6w)


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

