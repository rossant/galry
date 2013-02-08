Low-level API
=============

This layer is an object-oriented wrapper around OpenGL 2. It implements
the most common features. It is meant to be lightweight, simple and
easy-to-use. Only the programmable pipeline is available.

Context
-------

NOTE: this object may not be necessary at first.

The Context is an object containing all OpenGL objects used to render the
screen. It also implements the logic of the scene. OpenGL objects are added
with the `add` method. Then, the Context object provides three methods that
can be called from an OpenGL canvas (with Qt, wx, SDL, GLUT, etc.):
`initialize`, `paint`, `resize`. These functions can also be overriden for
customization. In Python, the Context provides decorator to simplify
this process.

Higher-level interfaces may not need to use the Context. All the functionality
should be implemented in the child objects, the Context being just a handy 
tool when using the low-level interface directly.

### Public methods

  * `Context.add(*args, **kwargs)`: add one or several objects to the context.
    The objects can be unnamed (then the variable name or an automatically
    generic numbered named is used) or named (keyword argument).
    
  * `Context.initialize()`: initialize the context. By default, initialize
    all objects included in the context. 

  * `Context.paint()`: paint all objects.

  * `Context.resize(width, height)`: resize the context.
    
    
Renderer
--------

This object allows to specify various rendering options: antialiasing, depth
buffer, etc., to clear the screen, etc.

### Public methods

  * `Renderer.set_antialiasing(options)`
  * `Renderer.set_depth(options)`
  * `Renderer.set_blend(options)`
  * `Renderer.enable(glname)`
  * `Renderer.clear(buffers)`
    
    
GLObject
--------

The GLObject is a base class for all objects that can be added to the context.


Shaders
-------

The Shaders objects allows to specify the shaders codes, to compile them,
activate/deactivate them.

### Public methods

  * `Shaders.set_vertex_shader(code)`
  * `Shaders.set_fragment_shader(code)`
  * `Shaders.add_uniform(name, dtype, size=None)`: `dtype` is [I]VEC[234]
  * `Shaders.set_uniform(name, value)`: set a value for a uniform.
  * `Shaders.add_attribute(name, vertex_buffer)`: link a shader attribute to
    a VertexBuffer object.
  * `Shaders.initialize()`
  * `Shaders.activate()`
  * `Shaders.deactivate()`
  * `Shaders.cleanup()`


VertexBuffer
------------

The VertexBuffer defines a vertex buffer which can be accessed as an attribute
in the vertex shader.

### Public methods

  * `VertexBuffer.set_dtype(dtype)`
  * `VertexBuffer.set_data(data)`
  * `VertexBuffer.initialize()`
  * `VertexBuffer.activate()`
  * `VertexBuffer.deactivate()`
  * `VertexBuffer.cleanup()`

  
IndexBuffer
-----------

The IndexBuffer defines an index buffer.

### Public methods

  * `IndexBuffer.set_data(data)`
  * `IndexBuffer.initialize()`
  * `IndexBuffer.activate()`
  * `IndexBuffer.deactivate()`
  * `IndexBuffer.cleanup()`
  

Texture
-------

The Texture defines a texture buffer which can be accessed as an sampler
in the fragment shader.

### Public methods

  * `Texture.set_info(ndim, dtype, params, index)`: set the texture
    information for the specified texture index (used for multi texturing)
    ndim is the number of dimensions of the texture (between 1 and 3).
    Generally dtype=UINT8. params is a TextureParams object with various information
    about the texture: filtering options, mipmapping, clamp options, etc.
  * `Texture.set_data(data, shape, index)`
  * `Texture.initialize()`
  * `Texture.activate(index)`: bind the texture.
  * `Texture.deactivate()`: unbind the texture.
  * `Texture.cleanup()`: release all resources.


Painter
-------

The Painter allows to render a vertex buffer.

### Public methods

  * `Painter.set_info(ptype, offset, size)`
  * `Painter.paint()`


PainterMulti
------------

The PainterMulti allows to render multiple primitives from a single vertex
buffer.

### Public methods

  * `PainterMulti.set_info(ptype, first, count, primcount)`
  * `PainterMulti.paint()`


PainterIndexed
--------------

The PainterIndexed allows to render from a vertex buffer and an index buffer.

### Public methods

  * `PainterIndexed.set_info(ptype, size)`
  * `PainterIndexed.paint()`


