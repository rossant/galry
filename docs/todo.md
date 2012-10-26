Galry: high-performance interactive 2D visualization in Python
==============================================================

Bug fixes
---------
  * GLSL: gl_* are deprecated, remove matrix transformation, gl_translate,
  etc and implement everything with shaders...
  MAYBE create a shader class?
  * texCoord[0] deprecated, rather use something like:
  
varying vec2 texCoord;

void main(void)
{
   gl_Position = vec4(gl_Vertex.xy, 0.0, 1.0 );
   texCoord = 0.5 * gl_Position.xy + vec2(0.5);     
}
  
  
  * identifier strings with '' instead of ""
  
  
Doc
---
  * automatic benchmark test
  * generate API reference

Code quality
------------
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
