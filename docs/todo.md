Galry: high-performance interactive visualization in Python
===========================================================

  * better way of switching pyside/pyqt
  
  * sometimes both pyqt and pyside seem to be loaded?? (mac and linux)

  * import galry.*** in the code instead of relative imports?

  * make unit tests work in ipython with pylab activated

  * include ony shader snippets in the scene, and include shader creation
    in the renderers

  * get rid of all enum and replace with strings
  * refactoring of interaction system, with EventProcessor objects which
    process events.
  * rename "bindings" to "mode"
  * process_action(action, parameters) in interaction manager for quick 
    interactivity
  * more modular interaction system (not having navigation related stuff in
    core classes)
  * key: string with "Key_%s"
  
  * high level interface

  * better handling of special_keywords
  
  * global color module in galry
  
  * check gl capabilities
  * check support for mipmapping
  
  
Automation
----------
  
  * automatic benchmark of cpu/gpu throughput and latency
  * automatic benchmark test
  * automatic screenshots of the examples to generate a gallery

  
Fixes
-----

  * bug: linux pyside segmentation fault
      * some update (2012/11/27): I could reproduce this issue on RedHat 5
        with a Nvidia cards (nvidia drivers, OpenGL 4.3) and pyside (EPD), 
        a PyQt4 package appearing not to be available on redhat. I could find
        two issues:
          * segmentation fault with pyside due to cursors, deactivating cursors
            does the trick but this should be investigated properly
          * another segmentation fault with OpenGL when a textured 
            primitive is drawn *after* a non-textured one. This happens with
            FPS for instance. Reversing the order of the visuals (texture first,
            non-texture then) does also the trick, but the precise reason is
            still unknown. It might due to the fact that the linux nvidia
            OpenGL driver does not like when a texture is bound (which
            happens upon visual creation) and a non-textured primitive is
            drawn right afterwards (there are no such bugs on windows). 
            Unbounding the texture does not appear to solve the problem. To be
            continued...
            TODO: simple minimalistic script which reproduces the bug
        Appart from that, everything appears to work correctly (tutorials
        and examples).
  
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
  * Linux with nvidia                           seg fault w PySide
  * MacOSX with nvidia                          OK

  
Later
-----

  * HDF5 viewer for long signals: use stride to implement a dynamic 
    multi-resolution undersampling method.
  * user preferences, with DEBUG option
  * better error messages when template is not correct (eg data is missing,
    size is missing, etc)
  * update text template to allow for several texts at different positions
  * opencl buffers and opencl/gl interop buffers
  * handle more complete data type (int 8/16/32 bits, floats, etc)
  * dynamic resampling with HDF5 stride for highly efficient interactive 
    visualization of multi-GB datasets (that cannot reside entirely in memory).
    Refinement: thread to update data on the GPU only when no action is occurring,
    for maximum perceived performance
  * check GL capabilities for different features
  
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

Ideas
-----
  * several plots (like subplot) with different widgets, linking possible
  * colormaps
  * new example: raster plot with sprites
  