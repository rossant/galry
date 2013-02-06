Modules
=======

The future version's scope will be slightly different from the original 
project. Whereas the original goal of Galry was to provide a high 
performance *plotting library*, the next version's goal will be to provide 
a high performance *visualization library*, which is more general. It will 
provide simple and flexible ways of designing fast interactive 
visualizations based on OpenGL and capable of handling tens of millions of 
points. The 2D plotting library will be an external module on its own 
(natively included in Galry in a separated sub-package like 
`galry.plotting` for instance).

In the long run, built-in modules may include:

  * 2D visualizations:
      * 2D plotting
      * huge signals viewers (with dynamic undersampling,
        HDF5 support, etc. to support huge data sets), e.g. multi-channel time
        dependent signals
      * high-dimensional data visualizer supporting arbitrary custom 2D
        projections
  * graph visualizer with dynamic layout (and OpenCL support?),
  * mesh visualizer,
  * volume rendering engine,
  * `z=f(x, y)` surfaces,
  * etc.
  
The idea is that visualizations that are sufficiently different should be
implemented in independent modules. 

Of course, the user will also be able to write his own visualization
application with Galry. The API will be the same than the one used to
write the modules described above.

Having Javascript and C++ implementation of Galry will allow to port all
these modules and applications on these languages without too much pain (at
least that's the long-term plan...).

