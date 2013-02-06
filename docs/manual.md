User manual
===========

Galry is a **high-performance interactive visualization library in Python**.

It offers a **high-level interface** for quickly visualizing large
datasets.

The **low-level interface** allows to create a fully customized GUI
for interactive visualization. It integrates with Qt, through either PyQt4 or 
PySide. Integration with other GUI systems may be considered at some point
(wx, etc.).

This manual gives a high-level introduction to both interfaces.
**The user interested in the practical details can go through the tutorials.**

Important note
--------------

Major changes to the library are to be expected in the coming months. The API
will probably change, especially the low-level interface. Galry is not
ready to be used in production yet, but can already be advantageously used as a
fast and efficient visualization toolkit capable of handling large datasets,
using the high-level interface.


High-level interface
--------------------

This interface is similar to the one offered by matplotlib. Only a very small
portion of matplotlib's features are currently implemented, because Galry
is not meant to generate publication-ready figures (it can merely export
the raw window as a PNG image).

Here are the available rendering functions.

  * `plot`: draw curves or scatter plot.
  * `text`: draw one or multiple strings of text with custom positions and
    colors.
  * `rectangles`: draw one or multiple rectangles.
  * `imshow`: draw an image.
  * `graph`: draw a graph with nodes and edges and custom colors.
  * `mesh`: draw a 3D mesh.
  * `barplot`: draw one or multiple bar plots.
  * `visual`: draw a custom visual.
  
Here are the available axes functions:
  
  * `axes`: specify the axes boundaries.
  * `xlim`: specify the x limits.
  * `ylim`: specify the y limits.
  * `grid`: display the grid by default.
  
Here are the available interaction functions:

  * `animate`: update the scene at regular intervals by calling a specified
    callback function.
  * `event`: bind an event to a callback method.
  * `action`: bind an action to an event or directly a callback method.
  * `figure`: create a new figure.
  * `show`: show the figure.

The details of these functions can be found in the tutorials/examples or
directly in the doc strings (in `galry/pyplot.py`, the API reference is not
done yet).


Low-level interface
-------------------

The low-level interface contains two parts:
a rendering module, and an interactivity module. The rendering module should
be thought as a module on top of OpenGL, which hides low-level implementation
details about OpenGL and exposes functions related to data and rendering.
The basic principles of OpenGL should however be understood in order to
customize all aspects of rendering.

THe low-level interface is meant to be used in script mode rather than in
interactive
mode. It allows to plot simple figures (scatter plots, curves, etc.) in
less than 10 lines of code. But it also gives you the opportunity to customize 
plots as 
much as you want. The integration of the plot within the GUI window can also
be fully customized (thanks to Qt).

Here, we give a **high-level overview of this interface** and, consequently, 
of the internal architecture of Galry.


### The `GalryWidget` class

The **main class that Galry provides is `GalryWidget`**.
It is a Qt widget deriving
from `QGLWidget` which is defined in Qt (available in PyQt and Pyside).
The `GalryWidget` displays an OpenGL context entirely controlled by
Galry through OpenGL.

First, some technical details about the internals of `GalryWidget`.
This widget inherits three important OpenGL-related methods from `QGLWidget`:

  * `initializeGL`: this method implements all OpenGL-related initialization,
    including uploading data on graphics card memory, compiling shaders,
    initializing OpenGL rendering engine.
    
  * `paintGL`: this method is called as soon as the widget view needs to be
    updated. It renders everything on the screen, starting from a black 
    background (the color can be customized). This means that everything is
    rendered again every frame: this is the standard way of rendering things
    with a graphics card. However, it is possible to upload data
    only once in 
    GPU memory at initialization, so that rendering is fast. If needed,
    data stored in GPU memory can also be changed at any time, during the
    lifetime of the widget.

  * `resizeGL`: this method is called as soon as the widget is resized. It
    automatically triggers a new rendering call. The OpenGL viewport size is
    also updated.

These methods are implemented in `GalryWidget` and should not be overriden.
However, they call special Galry methods that are meant to be overriden if
needed, and which are defined in companion classes, as we'll see later.

From the user point of view, the most important method of `GalryWidget` among
those that can be overriden is `initialize()`. This method is called in the 
widget constructor. Widget initialization (in particular, specification of 
the **companion classes**) happens there.


### Companion classes

By default, the `GalryWidget` class displays just a black empty rectangle.
The whole logic of the widget is implemented in several companion classes
that all handle a specific aspect of the widget. This allows to separate
the code into separate modules.

By default, there are three companion classes. These classes are meant to
be derived in order to implement the logic of the widget. In addition,
new companion classes implementing specific features can also be defined.
For example, one could implement a `SelectionManager` to handle selection of 
objects with the mouse. This custom companion class can then be reused in
different widgets. It should make modularity easier.

Any companion instance has access to all other companion
instances. The set of all companion instances can then be seen as a complete
graph, where each instance has access to all other instances.

The three default companion classes are:

  * `PaintManager`. This class handles everything related to rendering:
    data processing, uploading data on the GPU, initializing OpenGL objects,
    compiling shaders, etc.
    
  * `InteractionManager`. This class handles everything related to user
    interactions, and how they interfere with rendering.
    
  * `BindingManager`. This class handles the links between physical user
    actions with the mouse and keyboard, and interaction events. The
    association can be changed statically or dynamically. In addition, several
    interaction modes can be defined with different associations between
    actions and events (e.g. a navigation mode and a selection mode).

We'll go through the relevant methods of those classes later.

The creation of a new, custom Galry widget then involves the following steps:

  * Deriving one or several companion classes (e.g. `MyPaintManager`) by 
    overriding key methods.
    
  * Deriving the `GalryWidget` and overriding `initialize` to specify the 
    custom companion classes.
    
Also, helper functions are provided in order to directly show a window with
an automatically-created custom widget by specifying the companion classes,
without the need of explicitely creating a new class (see `show_basic_window`).


### The `PaintManager` companion class

The `PaintManager` class is the most important companion class. It specifies
what to render in the widget.


#### Visuals

The main method to override is `initialize`. This is where **visuals** are
created. A visual is a particular plot object, such as a set of points, of
curves, of rectangles, one image, one text string, etc. The key point is that
several *primitives* can be contained in a visual: several points in a 
scatter plot, several line segments in a curve, etc. So, **a visual is a
homogeneous set of primitives**. Primitives are defined in OpenGL and include
pixels, line segments, and triangles.
[The full list of primitives can be found for example 
here](http://www.informit.com/articles/article.aspx?p=461848).
Those primitives are described by a set of **vertices**.
A **vertex** is a vector of length 2, 3 or 4.

A visual is rendered *with a single call*
to an OpenGL command, so that rendering is fast. This explains why there is
the need for homogeneity within a visual. Also, let's note that within a 
visual, objects can be drawn independently (for example, different curves
that are not physically connected).

**In conclusion, a visual is meant to be
a big object in general**. It is not a good idea to define too many visuals
since that can really hurt performance.

*Very technical note: actually, it may happen that several OpenGL commands
are issued for a single visual. It occurs when the number of vertices is 
high, typically higher than 65,000. The reason is that the OpenGL buffers
cannot always be bigger than that. The set of vertices is then automatically
and transparently cut by Galry into multiple buffers, which are rendered
in sequence at each frame.*


#### Visual creation

A visual can either be created from scratch, or by specializing an existing
visual. Galry comes with a set of predefined visuals to plot curves, points,
images, point sprite textures, text, 3D meshes, etc. The user interested in
creating its own custom visual should look the code of the existing visuals.

Technically, a visual is defined by:
  * a set of *variables*, or *fields*, that have a name, a type, and various
    characteristics,
  * *vertex shader* and *fragment shader* source codes, that describe how
    data contained in the different fields will be eventually transformed into
    pixels.

##### Shaders
    
A **vertex shader** is a small program in a C-like language called
[**GLSL**](http://en.wikipedia.org/wiki/GLSL) that
is **executed once per vertex**. Vertex shaders execute in 
parallel across all vertices, using the high computational power of the 
GPU. A vertex shader takes some Visual fields as inputs, and
returns the final position of the current vertex. Execution of shaders can
be extremely fast thanks to the highly parallel architecture of the graphics
card.

A **fragment shader** is also written in GLSL, but executes after the vertex
shader, and **once per pixel**. It takes some variables as inputs, as well
as (possibly) some outputs of the vertex shader. It returns the final color of
the current pixel.


##### Visual fields

There are different types of visual fields:

  * **attributes**: an *attribute* is an array variable of size `N`.
    **All attributes in a given Visual share the same number `N`.**
    This number `N` is essentially
    the number of vertices. Also, there is one execution of the vertex 
    shader per vertex (so `N` executions), at every rendering call (so
    every frame). Examples of attributes: the position (coordinates of the
    points to render), the color of the points (if each point needs to have
    its own color), etc. Every variable that has one specific value per
    vertex is an attribute.
    
    When using *indexed rendering*, it is possible to
    use one vertex several times during rendering in order
    to save memory, so that the number of rendered vertices can be different
    from the number of vertices in the buffer (typically higher, since vertices
    are used several times).
    
  * **uniforms**: an *uniform* is a global variable, shared by all vertices. It
    may change at every frame, but it is global to the vertex and fragment
    shaders.
    
  * **varyings**: during the rendering process, the vertex shader is executed
    *once per vertex*. Then, the fragment shader is executed *once per pixel*
    (pixel of the rendered primitives). Since the fragment shader always
    executes after the vertex shader, the vertex shader can pass 
    information to the fragment shader through *varying variables*. They
    can be automatically interpolated when the pixels are between 2 or 3
    vertices (hence their names).
    
  * **textures**: a *texture* variable holds a texture data as a 3D array (with
    RGB(A) components) and can be accessed in the fragment shader in
    order to display it.
    
  * **indices**: an *index* variables holds a buffer of integer values which
    target vertices in all attributes. The number of rendered points is then
    the length of the index buffer rather than the length of the vertex buffer.
    
  * **compounds**: a particular type of variable that has no counterpart in
    the shaders. A *compound variable* allows to automatically change
    several visual variables according to a high-level value. They exist
    only for convenience for the user. For example, in the TextVisual,
    where characters are individually positioned on the screen, the
    text variable is a compound variable that affects the texture of the
    characters (i.e. the points), their particular position, etc.
    

##### Predefined visuals

Galry comes with a set of predefined visuals for convenient use. More
visuals may be added as the development of the package goes along.
Currently, available visuals are:

  * `PlotVisual`: generic visual for basic or advanced plotting. Any
    GL primitive is possible:
    
      * `LINES`: independent line segments,
      * `LINE_STRIP`: continuous signal as successive line segments,
      * `LINE_LOOP`: like `LineStrip` but as a closed polygon,
      * `POINTS`: pixels with arbitrary size,
      * `TRIANGLES`: independent triangles,
      * `TRIANGLE_STRIP`: successive triangles, two consecutive triangles
        sharing one side, useful for rendering any filled polygon,
      * `TRIANGLE_FAN`: successive triangles, all sharing the very first vertex.
        Useful for rendering discs.
        
    In addition, multiple independent primitives of the same type can be 
    rendered in the same visual (example: multiple signals as multiple
    `LineStrip`). Indexed rendering is also possible.
    
  * `RectanglesVisual`: multiple rectangles in a single visual.
  
  * `SpriteVisual`: one texture at multiple positions (e.g. scatter plot with
    special markers).
    
  * `TextVisual`: a single line of text.
  
  * `TextureVisual`: a single textured rectangle. It can accept filtering
    options and mipmapping. Non power-of-two and non-square textures are
    supported if the graphics card support them.
  
  * `MeshVisual`: visual example for 3D rendering, implementing
    3D/4D transformation matrices, basic lighting, etc. The developer
    interested in 3D rendering should take this visual as an example and
    customize it. This visual is well adapted for displaying a 3D mesh and
    move it around in 3D.
    
  * `GraphVisual`: a planar graph.
  
  * `BarVisual`: a set of bar plots/histograms.

    
##### Vertex shader example: particle system
    
Let's give an example of a *particle system*, where there is a number of 
independent particles, defined at any time by a position, a velocity, and 
a color. To achieve the highest performance possible, we want to execute this
system on the GPU. It means that vertex shaders are responsible for
updating the position of the particles at any time. So the visual could 
contain:

  * an *attribute variable* with the *initial position* of each particle,
  * an *attribute variable* with the *initial velocity* of each particle,
  * an *attribute variable* with the creation time of that particle,
  * an *uniform variable* with the current time,
  * etc.

For each particle, the vertex shader then gets the values of these variables
as inputs, and computes the current position of the particle with a formula
involving the initial position and velocity, and the current time.
The execution of this system is fast since the expensive part executes
entirely on the GPU. The graphics card is used optimally since the execution
of shaders is an embarrassingly parallel problem, with no communication between
threads.
    
This example is implemented in `examples/fountain.py`.


##### Fragment shader example: fractal viewer
    
Let's give an example of a *fractal viewer*, where a blank texture is rendered,
and the fragment shader computes the final color using an algorithm.
In the example of the Mandelbrot fractal, every pixel corresponds to a point
$z_0 \in E \subset \mathbb C$, and the color of that pixel depends on the
asymptotic
behavior of a discrete-time dynamical system defined by a recursive function:
$z_{n+1} = f(z_n)$. The fragment shader retrieves the coordinates of the
current pixel, then executes the dynamical system, and finally returns
the adequate color depending on the outcome of the system.
Once again, the execution of this example is optimal since it is an 
embarrassingly parallel problem.

This example is implemented in `examples/mandelbrot.py`.


##### Conclusion

Vertex and fragment shaders are widely used in real-time 3D video games,
but not so much in scientific applications, particulary when it concerns
2D rendering. Yet, they are extremely powerful for 2D rendering of huge
visuals with millions of points. They considerably widen the plotting 
possibilities of Galry.

To learn the OpenGL shading language, GLSL, a great, freely available
reference book is 
[Learning Modern 3D Graphics Programming](http://www.arcsynthesis.org/gltut/).
Also, 
[here is an introduction to shaders](http://cyrille.rossant.net/shaders-opengl/).



### The `InteractionManager` companion class

The `InteractionManager` class implements the logic of the interaction events
that are raised by user actions.

Some definitions first. An **user action** is an action performed by the user
through an input device such as a keyboard, a mouse, or through touch (the 
latter is not implemented yet). An **interaction event** is any dynamic event
that conveys some logic in the widget. An interaction event can interfere
with the rendering process. For example, zooming into the displayed data 
is an interaction event. The associated user action is, for example, 
moving the mouse while pressing the right button.

The implemented user actions are for now:

 * `Move`
 * `LeftClick`
 * `MiddleClick`
 * `RightClick`
 * `LeftClickMove`
 * `MiddleClickMove`
 * `RightClickMove`
 * `DoubleClick`
 * `Wheel`
 * `KeyPress`
 
At any time, an user action comes with some associated parameters, like the
relative displacement of the mouse for `Move`, or the pressed key
for `KeyPress`. In addition, all those actions can be modified by
a keyboard modifier such as Control, Shift or Alt.

A **binding** is a link between one user action and one interaction event.
More precisely, it links a pair (action, key modifier) to an interaction
event (there's also the pressed key for `KeyPress`). In addition,
a binding comes with a function that returns the action parameters (such as the
displacement of the mouse or the position of the cursor) that are relevant to
the associated interaction event. The result of this function is passed
to the interaction processor (see below).

An **interaction mode** is a set of bindings. For example, one could imagine
a *navigation mode* where moving the mouse while pressing the left button
corresponds to panning, whereas the same action corresponds to selection in
the *selection mode*.

The implemented interaction events are:

  * `SwitchInteractionMode`
  * `Pan`
  * `Zoom`
  * `ZoomBox`
  * `Reset`
  * `ResetZoom`

New interaction events can be defined.
  
As soon as an user action happens during the lifetime of the widget,
Galry finds the associated interaction event according to the
current interaction mode. Then, that interaction event and the relevant
action parameters (returned by the function specified in the binding)
are passed to the `InteractionManager`. This manager contains one or several
`EventProcessor`, which define handlers for different events. A handler
for an event is a method of the processor, which takes a parameter as an input
and perform some action in response to that event. Possible actions only
include changing the parameters of visuals for now, which already captures
most scenarios.

Processors can be reused in an a modular fashion. Each processor has access
to all other processors (every processor has a name, unique within a given
InteractionManager).


### The `BindingManager` companion class

The `BindingManager` companion class defines one or several interaction modes,
each mode being specified by a set of bindings between user actions and
interaction events.

This companion class does not need to be derived. Rather, a list of interaction
modes can be directly passed to `GalryWidget`. An interaction mode is 
implemented in a class deriving from `ActionEventBindingSet`. This class offers
an `initialize` method that can be overriden in order to set all the bindings.
A binding is set by the `set` method that accepts an `UserAction`, an
`InteractionEvent`, optionally, a keyboard modifier and the pressed key for
the `KeyPressAction`, and a function that returns the parameters related
to the user action and that are to be passed to the interaction processor.



