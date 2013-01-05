Galry: high-performance interactive visualization in Python
===========================================================

Before pre-release 0.1.0
------------------------

  * better handling of coordinates in high level callback
        window, view, data
  * event(fig, *params)
  
  
After pre-release
-----------------
  
  * include ony shader snippets in the scene, and include shader creation
    in the renderers

    
Refactoring
-----------

  * global color module in galry
  * better design for widget options (constrain ratio, activate_grid, etc)
  * rename visual= into name= in PM.set_data
  * rename extend into initialize (and have initialize_default)
  * rename "bindings" to "mode"
  * in interaction manager, better way to transform into transformed coordinates
    and data coordinates
  * better way of switching pyside/pyqt
  * remove compound variables, replace by methods in visual which take
    arguments as inputs and call set_data. the variables are then recorded
  * cascade of events (raise events in processors)
  * activation as events


Automation
----------
  
  * automatic benchmark of cpu/gpu throughput and latency
  * automatic benchmark test
  * automatic screenshots of the examples to generate a gallery

  
Fixes
-----

  * make unit tests work in ipython with pylab activated
  * try to reproduce bug with violation memory access when there are several
    widgets within a main window (concurrency issue in pyopengl?)  
  * fix bug in ipython notebook with empty arrays when loading a script
    for the first time
    
  
Tested
------

  * Windows 8 64 bits, AMD GPU
  * Windows 7 64 bits, nvidia GPU
  * Windows 7 64 bits, Intel HD 4000
  * Ubuntu 12.04 in VM, AMD GPU
  * Ubuntu 12.10 Nvidia Quadro GPU
  * Ubuntu 12.10 64 bits Nvidia GPU
  * MacOSX 64 bits with Nvidia


Later
-----

  * investigate the possibility of a MPL backend using galry: check out
    MPLGL by Chris Beaumont
  * adding new visuals dynamically
  * tutorials parts 2 and 3
  * HDF5 viewer for long signals: use stride to implement a dynamic 
    multi-resolution undersampling method.
    Refinement: thread to update data on the GPU only when no action is occurring,
    for maximum perceived performance
  * user preferences, with DEBUG option
  * better error messages when template is not correct (eg data is missing,
    size is missing, etc)
  * opencl buffers and opencl/gl interop buffers
  * handle more complete data type (int 8/16/32 bits, floats, etc)  
  * several plots (like subplot) with different widgets, linking possible
  * colormaps
  * support for wx?
    QT dependencies:
      * bindingmanager.py (convert from key string to 
        QT enum)
      * cursors.py (cursors from pixmap)
      * icons.py
      * galrywidget.py (QGLWidget)
    TODO:
      * abstract code related to icons/cursors
      * abstract code related to keyboard enum values      
      * abstract code related to the widget class
  * multifbos:
      * create one special visual which implements everything?
      * one FBO with 2 textures (prev)
      * one screen FBO with 1 texture
      
      * copy screen FBO => prev.1
      * partcl renders to prev.0
      * screen FBO = prev.0 + .9 * prev.1
  
  * finer control of the gl workflow (custom render method of visuals, or 
    custom gl calls within the paint function, etc.)
  * acyclic graph for references and avoid the restriction of order in
    the visuals definition
  * eventually: more object-oriented design...
  * complete separation between pure visualization and 2D plotting,
    plotting should be like an external plugin to the visualization toolkit
    (different folder)
  
  
Doc
---

  * generate API reference

  
Code quality
------------

  * identifier strings with '' instead of ""
  * PEP8
  * test coverage
  * lint
  * prepare for Python 3

  