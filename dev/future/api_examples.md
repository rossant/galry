API examples
============

This document contains several examples of how the API could be used.
The implementation should not start before the API has been designed in full
detail. It should also be kept in mind that these interfaces should be
adaptable in Javascript and C++.


Low-level interface
-------------------

Here is a simplistic example showing how this interface can be defined
to create OpenGL objects, customize the rendering process, and interface
it with a GUI library offering an OpenGL context.

    context = Context()
    context.antialiasing = True # with default parameters, 
                                # or = Antialiasing(prop1=val1, ...)

    # create a vertex buffer containing vec3 values
    mybuffer1 = VertexBuffer(ndims=3, dtype=FLOAT32, data=myarray)
    # alternative notation? VertexBuffer(VEC3, data=myarray)

    # create a 2D texture
    mytexture1 = Texture(ndim=2, shape=mytex.shape)
    # object-oriented interface, each object has some properties which can be 
    # set in the constructor or later
    mytexture1.data = mytex

    # add the objects in the context (might be done transparently with Python)
    # an exception is raised if there's a conflict with the names
    context.add(mybuffer1, texname=mytexture1)  # if a name is not provided as
                                                # a keyword argument, use the
                                                # variable name

    vs = VertexShader("""...""", myuniform1=Uniform(ndim=3, data=myvector))
    vs.myuniform2 = ...

    # add a frame buffer
    fbo = FrameBuffer()
    context.add(fbo)

    # add a painter, used to render primitives
    painter = Painter(ptype=LINE_STRIP, size=myarray.shape[0])
    
    # customize the rendering process
    @context.painter
    def paint(self):
        # get the buffer object from its name (equivalent to
        # self.get('mybuffer1')) and bind it.
        self.mybuffer1.bind()
        # loop through all painter objects
        for painter in self.get(Painter):
            painter.paint()

    # then, the following methods can be used in a GUI library:
    # context.initialize(), context.paint(), context.resize(width, height)


Visual interface
----------------

Visuals can be defined at compile time, and then can be easily added/removed
and shown/hidden in the scene.

    class TrianglesVisual(Visual):
        def __init__(self, data=None, color=None):
            # when several options are possible with the arguments (ie.
            # single color, multiple colors, etc.), subclasses of visuals
            # should be written instead of using lots of if statements
            vb = VertexBuffer(VEC3, data=data)
            vs = VertexShader("""...""")
            painter = Painter(ptype=TRIANGLES, size=data.shape[0])
            self.add(vb, vs, painter)

        # by default, the painter binds all buffers, and call paint on 
        # all painters

Then, to use visuals:

    # context from the low-level interface
    context = Context()
    
    # The scene contains the visual and has access to the context (low-level
    # API)
    scene = Scene(context)
    
    triangles = TrianglesVisual(data=myarray)
    scene.add(triangles)
    
    # then, the following methods can be used in a GUI library:
    # scene.initialize(), scene.paint(), scene.resize(width, height)
    



