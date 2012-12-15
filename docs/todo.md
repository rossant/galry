Galry: high-performance interactive visualization in Python
===========================================================

  * update examples with high level interface
  * grid: integrate data normalization
  * better design for widget options (constrain ratio, activate_grid, etc)
  * rename visual= into name= in PM.set_data
  * rename extend into initialize (and have initialize_default)
  * rename "bindings" to "mode"
  * in interaction manager, better way to transform into transformed coordinates
    and data coordinates
  * include ony shader snippets in the scene, and include shader creation
    in the renderers
  * check gl capabilities (eg mipmapping)
  * better way of switching pyside/pyqt
  * make unit tests work in ipython with pylab activated
  * tutorials parts 2 and 3
  * global color module in galry
  * adding new visuals dynamically

  
Automation
----------
  
  * automatic benchmark of cpu/gpu throughput and latency
  * automatic benchmark test
  * automatic screenshots of the examples to generate a gallery

  
Fixes
-----

  * try to reproduce bug with violation memory access when there are several
    widgets within a main window (concurrency issue in pyopengl?)
  
  * fix bug in ipython notebook with empty arrays when loading a script
    for the first time
    
  
Tested
------

  * Windows 8 64 bits, AMD GPU                  OK w PyQt4
  * Windows 7 64 bits, nvidia GPU               OK with #version0
  * Windows 7 64 bits, Intel HD 4000            OK    
  * Ubuntu 12.04 in VM, AMD GPU                 OK
  * Ubuntu 12.10 Nvidia Quadro GPU              OK
  * Ubuntu 12.10 64 bits Nvidia GPU             OK
  * MacOSX 64 bits with Nvidia                  OK


Later
-----

  * process_action(action, parameters) in interaction manager for quick 
    interactivity
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
  * new example: raster plot with sprites
  
  
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

  