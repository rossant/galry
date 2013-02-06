Here are a few notes about where Galry is headed in the months and years to come.

Long-term objectives
--------------------

The long-term goal is to provide a **high-level platform for OpenGL-based interactive visualization** that is:

  * fast,
  * scalable,
  * simple,
  * flexible,
  * portable.

### Fast

All today's devices are sufficiently powerful to provide fast interactive visualization. The main reason is that GPUs are now integrated in virtually any computing device: desktop computers, laptops, mini-PCs, tablets, mobile phones, etc. The main usage of GPUs is to enable video games on these devices. Galry aims at using efficiently this computing power to enable fast interactive visualization.


### Scalable

In the *Big Data* era, datasets containing tens of millions of points are now the rule rather than the exception. Galry is designed from the ground up to handle such large datasets using efficient data structures and algorithms. The objective is to keep the visualization fast no matter how big the underlying data is. The hardware should be the only limitation through the amount of available memory and computing power.


### Simple

Most existing visualization libraries are either powerful and difficult to use, or limited and easy to use. Galry is meant to be *powerful enough and simple enough*. Although complex 3D video games are beyond the scope of the library, any reasonably complex visualization should be handled by Galry. The object-oriented interface will offer a straightforward way of creating and manipulating visual objects interactively.


### Flexible

A high-level interface will offer easy ways to access to the most common features.
Galry will also provide direct access to low-level OpenGL functions (through a dedicated thin low-level interface on top of OpenGL) to let the developer customize all aspects of the rendering process. The same foundations will allow to write a fast plotting library (like Matplotlib or Matlab), a volume rendering engine, or a simple video game.


### Portable

Galry is primarily meant to work on desktop PCs (Windows or Unix) but may also be extended on mobile devices in the future. The open standard OpenGL is widely available on most devices and is the best option for writing a portable hardware-accelerated interactive visualization library.


Languages
---------

Although Python is currently the primary language, we could imagine implementations in at least two other languages: Javascript and C++. Javascript would allow Galry to work in the *browser* though WebGL. C++ would allow it to run on *mobile devices* (especially Android), since mobile WebGL support is still lacking (but that may change in the future). Sharing the maximum amount of code for one application between Python/desktop, Javascript/Web and C++/mobile devices is a major long-term objective.

This may be difficult to achieve as these are very different languages. There are mainly two different issues: static interoperability and dynamic interoperability. In the first case, the visualization is determined at compile-time. Writing the same application in two different languages requires to implement the same code twice, but that should not be that painful if the API and the data structures are well thought. In the second case, the specific visualization is dynamic and not determined at compile-time, so that the API must provide functions to change the scene dynamically. These features alsso need to be implemented in all supported languages.

This goal should influence the design of the library (architecture and interfaces). The integration of Galry in the IPython notebook will be a medium-term goal.


Interfaces
----------

A low-level interface will give a simpler access to OpenGL than the OpenGL standard, which is complex and verbose.

A high-level interface will give object-oriented access to visual objects and interactivity.

A medium-level interface will link the two.

The design of these interfaces will be done simultaneously.


Plotting
--------

Curve plotting should be thought as an independent module on top of the visualization interfaces.


