User manual
===========

Galry is an highly efficient hardware-accelerated interactive 2D visualization
package in Python.

Galry offers an high-level interface for quickly visualizing large 2D
datasets. It can be used either in script mode, or in interactive mode
with IPython. It integrates smoothly with the QT event system of IPython
so that you can interact with the plotting widget from the IPython console.

The low-level interface lets you create a fully customized GUI
for interactive visualization. It integrates with QT, through either PyQT or 
PySide. Integration with other GUI systems may be considered at some point
(wx, etc.).

This user manual gives a wide, high-level introduction to both interfaces.
**The user interested in the practical details can go through the tutorials.**


High-level interface
--------------------

This interface is not done yet.


Low-level interface
-------------------

### The `GalryWidget` class

Galry provides a QT widget class called `GalryWidget`. This class derives
from `QGLWidget` which is defined in QT (available in PyQT and Pyside).
The `GalryWidget` displays a rectangle entirely rendered by OpenGL.

This widget inherits three important OpenGL-related methods from `QGLWidget`:

  * `initializeGL`: this method implements all OpenGL-related initialization,
    including uploading data on graphics card memory, compiling shaders,
    initializing OpenGL rendering engine.
    
  * `paintGL`: this method is called as soon as the widget view needs to be
    updated. It renders everything on the screen, starting from a black 
    background (the color can be customized). This means that everything is
    rendered again every frame: this is the standard way of rendering things
    with a graphics card. However, the data can be uploaded only once in 
    GPU memory at initialization, so that rendering is fast. If needed,
    data stored in GPU memory can be changed at any time, at the expense of
    performance.

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
that all handle a specific aspect of the widget. This lets you separate
the code into separate modules.

By default, there are three companion classes. These classes are meant to
be derived to implement the logic of the widget. In addition,
new companion classes implementing specific features can also be defined.
For example, one could implement a `SelectionManager` to handle selection of 
objects with the mouse. This custom companion class can then be used in
different widgets.

Any companion instance has access, through attributes, to all other companion
instances.

The three default companion classes are:

  * `PaintManager`. This class handles everything related to rendering:
    data processing to put user-provided data into a GPU-friendly form,
    initialization of the plotting objects, etc.
    
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


### The `PaintManager` companion class

The `PaintManager` class is the most important companion class. It specifies
what to render in the widget.

Once again, the main method to override is `initialize`. It makes calls
to specific methods in `PaintManager` that define objects to be rendered.
An important point is that the number of calls to these methods in 
`initialize` should be as low as possible for performance reasons. Ideally, 
**only one call should be done here**. It is however possible to plot several
independent objects of the same type in a single call, as we'll see below.

There are two sorts of methods in `PaintManager` that give two different
ways of defining data: the easy way and the hard way.

#### The easy way

Three helper methods are available for now.

  * `add_plot`: this method adds a new plot. Arguments include x and y
    coordinates as 1D or 2D arrays, according to whether a single object
    or several objects (one per line in the arrays) should be plotted.
    Types of plots closely follow OpenGL primitive types: points, lines,
    triangles, etc. The color can be identical for all points, or can
    be specified individually for every point.
    
  * `add_textured_rectangle`: this method displays a texture. The texture
    is specified as a `N x M x 3` array (RGB components).
  
  * `add_sprites`: this method displays a single texture at different positions
    in a very efficient way. This is a common technique in 2D video games.
    Arguments include the texture, its size, and the sprites positions.
    
The reader can refer to the reference API for complete details about these
methods. Also, 
[the list of primitives can be found for example 
here](http://www.informit.com/articles/article.aspx?p=461848).

#### The hard way

This way is more complicated, but allows full customization and gives full 
control on the GPU rendering process.

Some definitions first.
We call a **dataset** a set of Numpy arrays of size `N` or `N x D` with `D` 
between 2 or 4, all arrays having the same `N`. Each array is called a
**buffer** and is associated to that dataset. The role of a dataset is 
eventually to render `N` points on the screen. `N` can be large (like several
millions), and even _should_ be large, so that the number of datasets in
a single widget is as low as possible (ideally one).

A dataset is created with `create_dataset` which accepts as arguments `N`,
the default color, the primitive type, and the shaders (see below).
It also accepts a bound list, containing the indices separating the different
objects to be rendered as independent primitives.
A buffer is added to a dataset with `add_buffer` which accepts a buffer name
and buffer data as arguments.

The data defining the positions and color of those points is contained in any
number of buffers (even though more buffers always implies a slight decrease in
performance). The simplest situation is when a single buffer contains the x, y 
coordinates of the points. The second simplest situation is when one buffer
contains the positions, and another one contains the colors of all points.

The situation can be more complicated: the position and color of the points
could depend on several factors, each defined by a specific value for every
point. For example, in a particle system, each particle's position is defined
by its initial position, initial velocity, different forces, time, etc. The
final position is calculated from those values through a simple algorithm
involving a mathematical formula.

It is the role of the **vertex and fragment shaders** to calculate the final
positions and colors of the points from the data buffers.
Technically, a shader is a small program written in a C-like low-level language
called GLSL (OpenGL Shading Language). It is compiled and executed on the GPU
at every rendering pass (every frame). It is executed independently for all
points (vertex shader) or pixels (fragment shader) on the graphics card.
It is an embarassingly parallel operation and therefore shaders fully exploit
the power of the graphics card.

**The vertex shader computes the position of every point**. In a given
rendering pass, it is executed `N` times, once per point in the dataset.
It takes as inputs
the values of every data buffer at the current point, as well as global
variables that are the same for all points (they are called **uniforms** in
OpenGL). It ouputs the position of the point. It can also
output other data that will be passed to the next programmable stage
in the graphics pipeline, namely the fragment shader.
  
**The fragment shader computes the color of every pixel**. In a given
rendering pass, it is executed once per pixel belonging to a rendered
primitive. It takes as inputs
all outputs of the vertex shader, along with the default color of the point
if it was specified (simplest situation). It outputs the color of the pixel.
The fragment shader has also access to the normalized
coordinates of the current pixel within the rendered primitive. This permits
to display a texture on a primitive, where the color of the pixel is obtained
by the color of the texture at the corresponding position.

Default shaders are provided in the easy way, corresponding to the three
simplest situations (position only, position and color, texture). You can
write and provide your own shaders to get full control of the graphics card.
This is an advanced feature, but it considerably widens the rendering 
possibilities. The interested reader should first take a look to the relevant
examples. They include a GPU-based particle system (implemented in a vertex
shader) and a Mandelbrot fractal interactive viewer with dynamic zooming 
(implemented in a fragment shader). To learn GLSL, a great, freely available
reference book is 
[http://www.arcsynthesis.org/gltut/](Learning Modern 3D Graphics Programming).


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

 * `MouseMoveAction`
 * `LeftButtonClickAction`
 * `MiddleButtonClickAction`
 * `RightButtonClickAction`
 * `LeftButtonMouseMoveAction`
 * `MiddleButtonMouseMoveAction`
 * `RightButtonMouseMoveAction`
 * `DoubleClickAction`
 * `WheelAction`
 * `KeyPressAction`
 
At any time, an user action comes with some associated parameters, like the
relative displacement of the mouse for `MouseMoveAction`, or the pressed key
for `KeyPressAction`. In addition, all those actions can be modified by
a keyboard modifier such as Control, Shift or Alt.

A **binding** is a link between one user action and one interaction event.
More precisely, it links a pair (action, key modifier) to an interaction
event (there's also the pressed key for `KeyPressAction`). In addition,
a binding comes with a function that returns the action parameters (such as the
displacement of the mouse or the position of the cursor) that are relevant to
the associated interaction event. The result of this function is passed
to the interaction processor (see below).

An **interaction mode** is a set of bindings. For example, one could imagine
a *navigation mode* where moving the mouse while pressing the left button
corresponds to panning, whereas the same action corresponds to selection in
the *selection mode*.

The implemented interaction events are:

  * `SwitchInteractionModeEvent`
  * `PanEvent`
  * `ZoomEvent`
  * `ZoomBoxEvent`
  * `ResetEvent`
  * `ResetZoomEvent`

New interaction events can be defined.
  
As soon as an user action happens during the lifetime of the widget,
galry finds the associated interaction event according to the
current interaction mode. Then, that interaction event and the relevant
action parameters (returned by the function specified in the binding)
are passed to the interaction processor that is implemented in the 
`InteractionManager`. This processor handles this event and makes the
relevant changes to the different companion objects (such as the 
`PaintManager`) in order to implement the logic of the event. The processor
is implemented in the `process_event` and `process_extended_event` methods
of the `InteractionManager`. The former method processes exising events
(related to navigation essentially), whereas the latter can be overriden
in order to handle new, custom interaction events that are not part of
galry.


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



