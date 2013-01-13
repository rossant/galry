0.1 milestone: minor improvements, doc, tutorials
0.2 milestone: major refactoring. Modular architecture:

    Plotting library
        plotting-oriented API
    Visual layer
        object-oriented description of the scene and the interactions
    GL middleware
        provide a simpler, data-focused API to OpenGL
    OpenGL
        

GL middleware
-------------

Python interface that provides access to most of the OpenGL functionality
but much simpler than pure OpenGL.

Objects:
  * Attribute
  * Texture
  * Uniform
  * Index buffer
  * Varying
  * Frame buffer
  * Shader
  * SimplePainter
  * IndexedPainter
  * CLBuffer

Controller objects:
  * Initializer
  * Resizer
  * Painter

They contain an ordered list of hooks, which are called during each phase.
For example, the Painter can contain the following hooks:

  * Clear
  * Shader.bind
  * Attribute.bind (all attributes, or specific attributes)
  * Texture.bind
  * Change frame buffer
  * SimplerPainter
  * Other attribute.bind
  * IndexedPainter

This way, one can precisely control the flow of the rendering process.
This interface should also provides way to dynamically change things, such as
variable data, or other parameters. For example, interactive navigation would
be implemented by updating the scale and translation uniform values.

Also, this interface should be defined independently from the language, so that
it could also be implemented in Javascript/WebGL for instance. Actually it
should be serializable.

At this level, there should be no notion of visuals at all. Just simplified
access to OpenGL, no abstraction besides pure OpenGL objects.

Most objects have the following methods:
  
  * initialize: create the relevant OpenGL objects
  * load: load the data associated to the objects
  * bind: bind the objects in OpenGL
  * update: update the objects or the data
  * finalize: release all resources
  
The Painter objects have the following methods:

  * initialize/update: define/change the options (primitive type, size, etc.)
  * paint

Every object has a unique identifier.
  
The interface should contain methods to:

  * access objects from their identifiers,
  * access all objects of a given class,
  * access all objects of a given class except a list of identifiers

Interface:

  * define the list of all objects
  * define a list of named parameters (rendering options, data, variable values)
  * change some parameters values
  * define the controller hooks
  * change the hooks
  
Support for OpenCL should be built-in, with specific CL buffers and ways to
do interop between CL/GL objects.

Context
    contains a list of objects
    add_object
    get

Controllers
    Initializer
    Resizer
    Painter
        add_hook

Manager
    Context
    Controllers
    Updater

Dynamic Update:
    change an object's attribute
    add new object
    add Painter hook
    remove Painter hook
    
Write a bunch of examples with this interface.
This module should be completely independent, and could even be in a 
standalone git repository.


Visual layer
------------

This layer communicates only with the GL middleware (GLM).
Visuals: objects that define several GLM objects (attribute, uniforms, shaders,
etc.) and Painter objects. There's also a default hook (bind all attributes,
paint all visuals, etc.). A visual can contain several painter objects.
Objects can refer to other objects: visual_id.var_id.
Interaction should also be defined here: adding/removing a visual, updating a
visual's variable, changing the hooks, etc.


Plotting library
----------------

Define plotting-oriented visuals and simple interaction methods.
Line, points, grid, shapes, transformations.



Examples
--------

Ensure that the following examples could work nicely with the new architecture
(they encompass much of the final functionality)

  * A 2D plot with lines and points, interactive navigation, grid.
  * A planar graph with dynamic force-based layout algorithm and manipulation
    of nodes, buffer sharing between nodes and edges, indexed painting, etc.
  * Volume rendering example with 3D texture and special shaders


Meta
----

Major refactoring: restart from scratch.
Design the modules as standalone as possible.
Python 3 ready, PEP8.
Independent Unit tests for the different layers: the GLM should have specific
unit tests with a mechanism for comparing the OpenGL output with images.
The visual layer should be tested independently from the GLM layer, ie a mock
testing GLM layer should be created that does not use OpenGL at all.
The unit test structure and a few examples should be done BEFORE the 
implementation.

  * First step: define precisely the interface of all layers and
    objects.
  * Second step: write as many unit tests as possible, and some examples.
  * Third step: implementation.
  



  


