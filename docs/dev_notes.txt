Implementation notes
====================

The base class GalryWidget contains plotting methods that can be 
conveniently used by child classes to plot anything on the screen.

Two internal methods are important: initializeGL() and paintGL().
  * initializeGL() is called at initialization time. It is the right place to
    initialize buffers, VBO, etc.

  * paintGL() is called each time the window needs to be redrawn. It makes
    calls to all plotting commands.

Companion classes
-----------------

The GalryWidget uses several companion classes (modules) to render data and
to handle user interaction. They can be overriden by derived classes of
GalryWidget.

  * PaintManager: this class handles rendering (data normalization, transfer
    on GPU using OpenGL vertex buffer objects, rendering commands, etc.).
  
  * BindingManager: this class handles the different interaction modes, each
    mode being defined by a set of bindings between user actions and interaction
    events.
    
  * InteractionManager: this class processes events raised by user actions
    (see below).
    
Data coordinates
----------------

galry can display static data only, meaning that the only dynamic part comes
from interactive navigation of the same data.

There are several coordinate systems available:

  * The _data coordinate system_. It corresponds to the coordinates of the data.
    It is unnormalized and depends directly on the data passed to the widget.

  * The _normalized data coordinate system_. It is like the data coordinate
    system, but normalized so that the data lies in [-1,1]^2. It is necessary
    for correct OpenGL rendering. This coordinate system moves when the user
    navigates into the data.
    
  * The _window coordinate system_. It is always fixed regardless of the
    navigation transform. (0,0) is the screen center, the corners are
    (+-1, +-1).


Initialization
--------------

At initialization, the PaintManager.initialize() method is called. It loads 
relevant data on the GPU.

Rendering loop
--------------

The rendering system in galry is based on OpenGL. There is a rendering loop,
each iteration is called when the window needs to be refreshed (i.e. every time,
except when no user interaction nor window resizing happens - it is actually
more a callback than a real loop, the loop being implemented in a lower-level
language (C/C++) by PyOpenGL and PyQT).

The callback is implemented in GLWidget.updateGL(). Each iteration involves the
following steps:

  * Clear the screen with an uniform background color (black by default).
  
  * Transform the displayed objects using the world transformation matrix.
  
  * Paint data.
  
  * Paint overlays.

The transformation step depends on the user interactions (see next section)
through the InteractionManager, which basically transforms user actions
into OpenGL transformations.

The display step involves calls to OpenGL commands used to render data. The data
has been loaded during the initialization step, or can be reloaded during
this display step in the rendering loop.

The overlays require the transformation to be cancelled (the OpenGL state 
machine keeps track of every transformation during the rendering loop) so that
the overlays are always at the same position in the window (e.g. window 
coordinates instead of data coordinates).

Interaction system
------------------

A bit of terminology:
  * User actions: mouse moving, left/right click, wheel, keyboard, etc.
  * Keyboard modifiers: when pressing CRTL, SHIFT or ALT while doing another
    action.
  * Interaction events: navigation (panning or zooming), highlighting, selection

The interaction system in galry tries to decouple completely user actions from
interaction events, making links between the two through action-event
*bindings*.
  
User actions (like mouse or keyboard actions) are monitored through QT callbacks
defined in QWidgets (NOTE: QT is slowly moving away from QWidget and towards
QML). User actions are bound to interaction events, which are defined in galry.

Interaction system schematic:
    Action -> Binding -> Event raised -> Event processed in the rendering loop.

Properties of events:
  * Events can be arbitrarly linked to any user actions. The specific binding
    is customizable and may even be customized by the end-user.
    
  * When an event is triggered, it is processed immediately in the rendering
    loop and then discarded at the end of the loop iteration.
    
  * There can be at most 1 event at any iteration in the rendering loop.
  
Interaction loop:
As soon as the user makes something (with the mouse or the keyboard), the 
QWidget callback methods, overriden in GalryWidget, are called. These methods
do the following:

  * Raise the corresponding UserAction
  
  * Call GalryWidget.process_interaction().
  
The GalryWidget.process_interaction() method is responsible for processing
the event associated to the action. It does the following:

  * Find the corresponding event using the current action-event binding.
  
  * Call the event processor:
        interaction_manager.process_event(event, parameter).
  
  * Force an OpenGL update (i.e. call updateGL()).

The event processor is responsible for processing all events raised by user 
actions. The parameter is passed by GalryWidget.process_interaction() and is 
specified by a lambda function defined in the action-event binding. This 
lambda function takes a dict containing all variables related to all user 
actions (position of the mouse, last press position, etc.) and returns the 
parameter to be passed to the event processor. This lambda function hence 
makes the link between variables related to the user action (e.g. mouse state 
variables), and those related to the events (e.g. the amount of translation 
in the view). This helps decoupling between user actions and interaction 
events. 

The event processor (implemented in "interaction_manager.process_event()")
updates the InteractionManager internal state. The manager then has two 
occasions to actually influence the rendering in the rendering loop
(see the Rendering loop section):
one for applying the world transformation matrix, and one for displaying 
overlays (more occasions might be added in the future if needed).

Interaction modes
-----------------

Several interaction modes can be defined (e.g. navigation mode, selection mode,
etc.) in a totally customizable way. The idea is that at each interaction mode
is associated a particular set of bindings between user actions and interaction
events. For example, in the navigation mode, the dragging action could be
associated to panning, whereas in the selection mode, it could be associated
to drawing a selection box. The user can then switch between modes, and this
just changes the current set of bindings. This is handled by the 
BindingManager.
  
Some technical issues and their solutions (especially related to LongSignalPlot)
--------------------------------------------------------------------------------

In theory, Galry could simply work like this. There's an OpenGL 3D world, 
with a fixed horizontal orthographic camera, at position (0, 0, -1) and looking 
at (0, 0, 0). The data, loaded on the GPU vertex buffer upon initialization, 
is drawn in the Z=0 X,Y-plane. When interacting with the data, the data is 
transformed with a translation (paning) and scaling (zooming in and out). This 
is pretty much how it's working, except that there are several technical 
complications that make the implementation harder. The goal is however to try 
hiding those details from the exposed programming interface.

The technical issues are the following:
  
  * The data to visualize can be really big, so that it may not be possible to 
    load it entirely on GPU memory or even system memory. Yet, one typically
    wants to visualize the full data interactively.
  
  * When viewing a t -> f(t) function with t spanning a large time interval, 
    there can be a loss of precision in the displayed data due to floating point 
    issues. For example, when visualizing the [1e9,1e9+1] interval (with
    sampling frequency, say, 10 kHz), the x values are translated back to [0,1] 
    so that data is within the camera field of view. When zooming in, one can 
    then observe a loss of precision that severly harms visualization.
  
  * A related problem is that there are display issues with OpenGL when using 
    transformation matrices that contain large values.

Chosen solutions to those issues are the following:
  
  * To allow the data to not be fully loaded on GPU memory: Implement a data 
    paging system. A minimum zoom-in, corresponding to a maximum viewbox, is 
    chosen. This sets the size of the GPU data buffer. When the requested 
    transformation implies that the viewbox is not fully included within the
    data buffer, a new data load is requested from system memory to GPU memory.
  
  * To allow the data to not be fully loaded on system memory: Use the HDF5 data 
    file format, so that when requesting a new data load, the data is loaded 
    transparently from the hard drive rather than the system memory.
  
  * Renormalize data to [-1,1]², so that the initial viewbox matches this
    square.
  
  * Additionnaly, when loading data where x is in [x0, x1], rather generate 
    values in [0, x1-x0] which are more precise, and modify the translation 
    accordingly.


Misc notes
----------
    
  * HACK for text rendering: text rendering is done with GLUT. There are
    two implementations of GLUT possible with PyOpenGL. One has the right 
    routine to display text, the other not. By default, the wrong implementation
    might be used (at least on Windows). The trick to make PyOpenGL use the 
    correct one is, on Windows, to rename:
    C:\Python27\Lib\site-packages\OpenGL\DLLS\glut32.dll => glut32.dll!
    This way, PyOpenGL will fall back on the correct one (freeglut).
    see: http://choorucode.wordpress.com/2012/04/28/using-freeglut-calls-with-pyopengl/
    