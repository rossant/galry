Galry: high-performance interactive 2D visualization in Python
==============================================================

  * create_dataset, default size in template

  * data_template: integrate set_default_data into add_*

  * create TextTemplate
      * implement text with texture atlas
      * idea: first, pregenerate a KxKxN matrix where M[:,:,i] is the texture
        of character i (and save it into a binary file for instance).
        K is the size of each character, N the number of characters. Then
        it is straightforward to obtain dynamically and efficiently a
        2D texture with any string. This is all done on CPU with numpy, then
        the whole texture is transferred on the GPU.
        To generate the original matrix, one possibility is to use matplotlib:
        display characters in a window, save everything into PNG images of
        fixed size. Then, load all images and create a single texture
  * remove overlays
  * create RectangleTemplate



  
Doc
---
  * automatic benchmark test
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
