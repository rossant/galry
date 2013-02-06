Features that should be easily supported
========================================

Here is a list of features that are or aren't currently supported in Galry
and that should be supported in the future version. In particular, the decision
to include most of these features was made late in the architecture design,
so that their implementation required some tricks and hacks that prevent to 
have a nice and well-thought global architecture.
Taking these constraints into account in the early design of the future version
will make things easier.

  * aliasing
  
  * enable/disable depth
  
  * Option to constrain the ratio of the window. When resizing the window,
    there are several possibilities: stretch the viewport to match the window,
    or keep the viewport ratio fixed. In the latter case, there are several 
    ways about how the new viewport can be changed. A possibility can be
    to implement projection matrices that can work for 2D or 3D.
    
  * FPS
  
  * automatic save of the images during the rendering process
  
  * render loop with specified time step
  
  * auto destruction of the window after a certain period



