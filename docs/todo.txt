Galry: high-performance interactive 2D visualization in Python
==============================================================

Code quality
------------
  * generate API reference
  * automatic benchmark test
  * PEP8
  * unit testing
  * test coverage

Ideas
-----
  * several plots (like subplot) with different widgets, linking possible
  * colormaps
  * new example: raster plot with sprites
  
High level interface
--------------------

Different specialized widgets with user-friendly interface.

  * plot(x, y, options)
    options = '-' or ','
    color: 'r', 'g' , etc.
    
  * barplot(h)

  * Longsignal plot: for viewing long analog continuous signals that 
    cannot fit on screen or in system memory (hdf5). An horizontal scrollbar
    allows to scroll along time, new data is loaded transparently
