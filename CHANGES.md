
2012-12-17 Update
-----------------
 
  * **High-level interface**: this new interface is a thin wrapper to the
    low-level interface. It provides a matplotlib-like interface which allows
    to easily add plots or any visuals on the scene, as well as defining
    custom handlers for events, and defining new events associated to 
    user actions.
  * All **tutorials** and **examples** have been updated to use this new
    high-level interface.
  * The **interaction system** has been refined and is now more modular.
    One can define standalone EventProcessors which register handlers
    for different events. Processors are then added in the InteractionManager.
    A given processor can be used separately in different managers and 
    widgets.
  * **New visuals**:
      * **GridVisual** (with grid, axes, ticks) but does not support
        automatic data normalization yet,
      * **BarVisual** (barplots, histograms) has been promoted from an example
        to a built-in, standalone visual,
      * **GraphVisual**, to plot graphs with colored nodes and edges (with
        reference buffer and indexed arrays for maximum memory efficiency),
      * **MeshVisual** to display a 3D mesh (along with a Python function to
        load a .OBJ ASCII object).
  * New Help option (H keyboard shortcut) to automatically display all bindings
    between user actions (mouse, keyboard, etc.) and events. It is quite
    convenient because it is dynamically and automatically generated
    as a function of the bindings in the current interaction mode.
  * Removed obsolete examples and restructured completely the tutorials.
    There will be three parts in the tutorials:
      * high-level interface for plotting and custom visuals,
      * high-level interface for custom interaction management,
      * low-level interface.
    Only the first half of the tutorials are done for now.
  * New tutorials/examples: raster plot with spikes as sprites, photo gallery:
    provide a folder with JPG images as argument and you can visualize all
    your photos in fullscreen.
  * Fixed segmentation fault on Linux with NVidia drivers which occurred
    when non-textured visuals where rendered before a textured visual.
  * Got rid of all enumerations, which added complexity and harmed readibility.
    It was not such a good idea to use them in the first place.
    Python ain't C#.


2012-12-02 Update
-----------------

  * The rendering engine has been entirely rewritten in order to increase
    the separation between the scene creation logic, and the actual GL 
    rendering.
  * This new architecture will make it easier to integrate Galry into the
    **IPython notebook**. A highly experimental proof of concept has been
    implemented and gives encouraging results (see the `experimental` folder).
  * A **high-level interface**, much similar to the pylab interface of
    matplotlib,
    will be available later. Using Galry for high-performance interactive 
    visualization with a given plotting script using matplotlib will just be
    a matter of replacing `import pylab as plt` with
    `import galry.plot as plt`.
  * It will be possible to automatically convert a Python plotting
    script using Galry to **WebGL/Javascript code** for integration within a
    standalone webpage. No Python required for running the webpage, just
    a WebGL-enabled browser.
  * The interaction system will be improved soon and the interface will
    probably change.
  * New features:
      * More efficient data updating system: before, the data could be changed
        at the condition that the size of all attributes and textures were kept
        unchanged. This limitation has fortunately disappeared.
      * Support for **texture filtering** options (including mipmapping).
      * Support for 1D and non-square textures.
      * Support for reference buffers: the same memory buffer on the GPU
        can now be used for several visuals in order to save memory
        (useful for graph rendering, where edges and nodes share the same
        memory buffer on the GPU).
      * Support for indexed rendering (index buffers). Useful for graph
        rendering where the edges are specified with indices targetting
        node positions.
      * New example: dynamic planar **graph rendering** with a simple CPU-based
        physics engine.
      * New example: **3D mesh** viewer (adapted from an example in Glumpy).
      * New example: **Pong video game**.
  * The 
    [context of the development of Galry can be found on this blog post](http://cyrille.rossant.net/galrys-story-or-the-quest-of-multi-million-plots/).

    
    