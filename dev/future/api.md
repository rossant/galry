API notes
=========

The interface will be portable, i.e. not tied to Python. Using and
object-oriented paradigm may help achieving this goal.

The low-level interface is a thin wrapper on top of OpenGL, with less
boilerplate code than pure OpenGL calls. It could be used in other
visualization projects too. 

The visual interface is an object-oriented interface specifying
a particular visualization. It is written on top of the low-level interface.
Moreover, the low-level interface should also be directly accessible
from this layer.

The interactivity interface should be independent from the other interfaces.
It will implement a simple event system which is independent from any backend
GUI toolkit.

The high-level interface will come in two flavors: object-oriented, and
script-oriented. The latter interface will just be a wrapper of the former.


Low-level interface
-------------------

This interface closely follows the OpenGL 2.0 API, or at least a subset
of it. Here are the features that it will support:

  * Vertex shaders
  * Fragment shaders
  * Vertex buffer objects
  * Index buffers
  * Textures
  * Uniform and uniform arrays
  * Frame buffer objects

These features should enable the vast majority of 2D and 3D visualization
capabilities of OpenGL 2.0.

There will be an option to toggle between ES and Desktop OpenGL versions.
This low-level API will offer exactly the same methods for both versions.
In particular, the user-provided GLSL code will be automatically adapted
for OpenGL desktop or ES version (it will just contain the code of the main 
and some external functions, not variable declarations).

In the current version, this functionality is broadly speaking implemented
in GLRenderer.


Visual interface
----------------

This is maybe the most challenging interface among the three. It should be
simple enough and flexible enough. In particular, it should allow direct access
to the low-level interface if needed, and offer a simpler interface for the
most common use cases.

The central notion in this layer is that of *visual*. A visual is a visual 
object defined by several OpenGL objects (defined in the low-level API):
buffers, textures, shader codes, etc. It is also characterized by a `paint`
method, which can be simple (default) or more complex.

Globally, there will be methods to manipulate visuals in the scene. In
particular, the final `paint` method can also be overriden.

There will also be facilities to change dynamically the scene: change the
visual attributes, show/hide visuals, delete or add new visuals dynamically.

In the current version, this functionality is broadly speaking provided
in the Visual module.


Interactivity interface
-----------------------

This interface will implement a simple event system, used for interactivity,
animation, etc. It will be possible to launch events in cascade (an event
which raises another event). An integration of an asynchronous system (using
different threads) may also be considered at this level.


High-level interface
--------------------

The high-level interface allows to link the visualization layer with the
interactivity layer.

In the current version, this functionality concerns broadly speaking 
the different managers, and the scripting interface.


