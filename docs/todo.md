Galry: high-performance interactive 2D visualization in Python
==============================================================

  * REFACTORING: data holder, template.size, allow dynamic change of template
    size, scenes, etc.
  * javascript standalone version of the renderer and the deserializer
  * python/javascript should be able to accept JSON templates/scenes
  
  * try to reproduce bug with violation memory access when there are several
    widgets within a main window (concurrency issue in pyopengl?)
  * user preferences, with DEBUG option
  * high level interface
  * bug: linux pyside segmentation fault
  * rename "bindings" to "mode"
  * process_action(action, parameters) in interaction manager for quick 
    interactivity
  
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
  