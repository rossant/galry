Galry: high-performance interactive visualization in Python
===========================================================

  * webgl renderer: one gl object per renderer (no global variable)
    and fix bug in ipython notebook with empty arrays when loading a script
    for the first time


  * get rid of all enum and replace with strings
  * refactoring of interaction system, with EventProcessor objects which
    process events.
  * rename "bindings" to "mode"
  * process_action(action, parameters) in interaction manager for quick 
    interactivity
  * more modular interaction system (not having navigation related stuff in
    core classes)
    
  
  * high level interface

Automation
----------
  
  * automatic benchmark of cpu/gpu throughput and latency
  * automatic benchmark test
  * automatic screenshots of the examples to generate a gallery

  
Fixes
-----

  * bug: linux pyside segmentation fault
  * try to reproduce bug with violation memory access when there are several
    widgets within a main window (concurrency issue in pyopengl?)
  
  
Later
-----

  * user preferences, with DEBUG option
  * better error messages when template is not correct (eg data is missing,
    size is missing, etc)
  * update text template to allow for several texts at different positions
  * texture1D
  * opencl buffers and opencl/gl interop buffers
  * handle more complete data type (int 8/16/32 bits, floats, etc)
  
Doc
---
  * generate API reference

Code quality
------------
  * identifier strings with '' instead of ""
  * PEP8
  * unit testing
  * test coverage
  * lint
  * prepare for Python 3

Ideas
-----
  * several plots (like subplot) with different widgets, linking possible
  * colormaps
  * new example: raster plot with sprites
  