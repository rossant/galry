Galry: high-performance interactive visualization in Python
===========================================================

  * make 3D example work

  * better error messages when template is not correct (eg data is missing,
    size is missing, etc)
  * gl renderer cleanup
  * test indexed array
  * graph with indexed array  
  * update text template to allow for several texts at different positions

  * javascript standalone version of the renderer and the deserializer
  
  * try to reproduce bug with violation memory access when there are several
    widgets within a main window (concurrency issue in pyopengl?)
  * user preferences, with DEBUG option
  * high level interface
  * bug: linux pyside segmentation fault
  
  * rename "bindings" to "mode"
  * process_action(action, parameters) in interaction manager for quick 
    interactivity
  * more modular interaction system (not having navigation related stuff in
    core classes)
    
  * texture1D
  
  * automatic benchmark test
  * automatic screenshots of the examples to generate a gallery
  
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
  