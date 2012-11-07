import sys
import inspect
import itertools
import time
import numpy as np
import OpenGL.GL as gl
import OpenGL.arrays.vbo as glvbo
from tools import enum, memoize, enforce_dtype, get_intermediate_classes
import ctypes
from debugtools import log_debug, log_info, log_warn
import templates as tpl
from dataloader import DataLoader, NP_GL_TYPE_CONVERTER, activate_buffer
from primitives import PrimitiveType, GL_PRIMITIVE_TYPE_CONVERTER


__all__ = ['PaintManager']


def get_template_initargs(template_class):
    """Return the list of accepted keyword arguments for the initialize method
    of `template_class`, including those of all the parent template classes.
    
    Arguments:
      * template_class: a class deriving from `DataTemplate`.
    
    Returns:
      * the list of all accepted keyword arguments of `initialize` and
        `initialize_default` of the template classes and its parent classes,
        up to the base `DataTemplate` class.
    
    """
    tplclasses = get_intermediate_classes(template_class, tpl.DataTemplate)[:-1]
    # this is the list of all accepted keyword arguments in the initialize
    # method of the template class and all its parent classes
    initargs = []
    for c in tplclasses:
        if hasattr(c, "initialize"):
            initargs += inspect.getargspec(c.initialize).args
        if hasattr(c, "initialize_default"):
            initargs += inspect.getargspec(c.initialize_default).args
    initargs = list(set(initargs))
    if 'self' in initargs:
        initargs.remove('self')
    return initargs


    
# PaintManager class
# ------------------                   
class PaintManager(object):
    """Defines what to render in the widget."""
    
    # Background color.
    bgcolor = (0., 0., 0., 0.)
    
    # Color of the zoombox rectangle.
    navigation_rectangle_color = (1.,1.,1.,.25)
    
    # Initialization methods
    # ----------------------
    def __init__(self):
        # current absolute translation offset, used because glTranslate is
        # relative to the current position
        self.current_offset = (0, 0)
        
        # list of datasets
        self.datasets = []

        # boolean indicated whether OpenGL has been initialized, the 
        # data has been loaded on the GPU, and the shaders have been compiled.
        self.is_initialized = False

    def initialize_gl(self):
        
        log_info("OpenGL renderer: %s" % gl.glGetString(gl.GL_RENDERER))
        log_info("OpenGL version: %s" % gl.glGetString(gl.GL_VERSION))
        log_info("GLSL version: %s" % gl.glGetString(gl.GL_SHADING_LANGUAGE_VERSION))
        
        # use vertex buffer object
        gl.glEnableClientState(gl.GL_VERTEX_ARRAY)

        # used for multisampling (antialiasing)
        gl.glEnable(gl.GL_MULTISAMPLE)
        gl.glEnable(gl.GL_VERTEX_PROGRAM_POINT_SIZE)
        gl.glEnable(gl.GL_POINT_SPRITE)
        
        # enable transparency
        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
        
        # Paint the background with the specified color (black by default)
        gl.glClearColor(*self.bgcolor)
        
    def initialize_default(self):
        """Default initialize method. Initializes the FPS (if shown) and
        the navigation rectangle."""
        if self.parent.display_fps:
            text = "FPS: 000"
            # create the FPS text dataset
            self.ds_fps = self.create_dataset(tpl.TextTemplate,
                fontsize=18,
                is_static=True,
                pos=(-.80, .92),
                text=text)

        # navigation rectangle
        self.ds_navigation_rectangle = self.create_dataset(
            tpl.RectanglesTemplate,
            is_static=True,
            color=self.navigation_rectangle_color,
            visible=False)
            
    def initialize_dataset(self, dataset):
        """Initialize a dataset after the end of `self.initialize`.
        
        This method takes the keyword arguments given in `create_dataset` and
        `set_data` and separates those to be passed to `template.initialize` 
        and those which are template data fields.
        This method initializes the template and the data loader, but does not
        upload anything on the GPU (this happens in `paintGL`).
        
        """
        # keyword arguments passed in create_dataset
        kwargs = dataset["kwargs"]
        
        # keyword arguments passed in set_data
        datakwargs = dataset["datakwargs"]
        
        # get the template class, not instanciated yet
        template_class = dataset["template_class"]
        
        # in kwargs, there can be arguments for template.initialize, others
        # for set_data. We distinguish them here by looking at the arguments
        # accepted by the `initialize` method of the template class and all 
        # its parent classes.
        initargs = get_template_initargs(template_class)

        # special handling of a few keyword arguments, which need
        # to be processed separately: they are not to be passed to `initialize`
        specialargs = ['bounds', 'primitive_type', 'default_color']
        
        # those kwargs not in initargs go in set_data
        kwargs2 = kwargs.copy()
        for arg in kwargs2:
            if arg not in specialargs and arg not in initargs:
                val = kwargs.pop(arg)
                # we do not update the value if it has been specified in
                # set_data, which comes after create_dataset (kwargs)
                if arg not in datakwargs:
                    datakwargs[arg] = val
        
        # we create the template class object here
        tpl = template_class()
        
        # now, kwargs contains the keyword arguments for initialize
        # but other arguments are needed from get_initialize_arguments
        supargs = tpl.get_initialize_arguments(**datakwargs)
        if supargs:
            kwargs.update(supargs)
        
        # special handling of a few keyword arguments, which we need to
        # directly pass as attribute values to the template before calling
        # initialize        
        for arg in specialargs:
            if arg in kwargs:
                # if one of those arg was passed in `create_dataset`, we set
                # the corresponding attribute in the template before we call
                # `initialize`.
                val = kwargs.pop(arg)
                setattr(tpl, arg, val)
                # we also record that property in the dataset    
                dataset[arg] = val
            
        # initialize the template object
        tpl.initialize(**kwargs)
        
        # finalize the template
        tpl.finalize()
        
        # set the special argument values in the dataset
        for arg in specialargs:
            val = getattr(tpl, arg)
            dataset[arg] = val
        
        dataset["template"] = tpl
        
        # create the loader
        dl = DataLoader(tpl)
        # datakwargs contains all the data arguments specified in
        # `create_dataset` or `set_data`.
        dl.set_data(**datakwargs)
        dataset["loader"] = dl
        
    def initialize_gpu(self):
        """Initialize the GPU by initializing the datasets, generating the
        shaders, and compiling them. No data is uploaded on the GPU yet."""
        for dataset in self.datasets:
            self.initialize_dataset(dataset)
            dataset["loader"].compile_shaders()
        self.is_initialized = True
 
    
    # Navigation rectangle methods
    # ----------------------------
    def show_navigation_rectangle(self, coordinates):
        """Show the navigation rectangle with the specified coordinates 
        (in relative window coordinates)."""
        self.set_data(coordinates=coordinates,
            visible=True,
            dataset=self.ds_navigation_rectangle)
            
    def hide_navigation_rectangle(self):
        """Hide the navigation rectangle."""
        self.set_data(visible=False, dataset=self.ds_navigation_rectangle)
        
        
    # Data creation methods
    # ---------------------
    def create_dataset(self,
                       template_class=None,
                       visible=True,
                       **kwargs):
        """Create a dataset. This method should be called in `self.initialize`.
        
        A dataset is an instanciation of a `DataTemplate`. A DataTemplate
        defines a pattern for one, or a homogeneous set of plotting objects.
        Example: a text string, a set of rectangles, a set of triangles,
        a set of curves, a set of points. A set of points and rectangles
        does not define a template since it is not an homogeneous set of
        objects. The technical reason for this distinction is that OpenGL
        allows for very fast rendering of homogeneous objects by calling
        a single rendering command (even if several objects of the same type
        need to be rendered, e.g. several rectangles). The lower the number
        of rendering calls, the better the performance.
        
        Hence, a dataset is defined by a particular DataTemplate, and by
        specification of fields in this template (positions of the points,
        colors, text string for the example of the TextTemplate, etc.). It
        also comes with a number `N` which is the number of vertices contained
        in the dataset (N=4 for one rectangle, N=len(text) for a text since 
        every character is rendered independently, etc.)
        
        Several datasets can be created in the PaintManager, but performance
        decreases with the number of datasets, so that all homogeneous 
        objects to be rendered on the screen at the same time should be
        grouped into a single dataset (e.g. multiple line plots).
        
        Arguments:
          * template_class=None: the template class, deriving from
            `DefaultTemplate` (or directly from the base class `DataTemplate`
            if you don't want the navigation-related functionality).
          * visible=True: whether this dataset should be rendered. Useful
            for showing/hiding a transient element. When hidden, the dataset
            does not go through the rendering pipeline at all.
          
        Returns:
          * dataset: a dictionary containing all the information about
            the dataset, and that can be used in `set_data`.
        
        """
        
        # Default template class
        if not template_class:
            template_class = tpl.DefaultTemplate
            
        # pass the `constrain_ratio` parameter to the parent widget
        if self.parent.constrain_ratio:
            kwargs["constrain_ratio"] = True

        # initialize the dataset object, for now just a placeholder for
        # all the information passed to `create_dataset` and `set_data`.
        dataset = {}
        dataset["visible"] = visible
        dataset["template_class"] = template_class

        # keyword arguments passed to `create_dataset`
        dataset["kwargs"] = kwargs

        # keyword arguments that may be passed to `set_data`
        dataset["datakwargs"] = {}
        
        # `self.datasets` contains the list of all defined datasets in the
        # paint manager.
        self.datasets.append(dataset)
        
        # we return the dataset, so that it can be used in `set_data` later.
        return dataset

    def set_data(self, dataset=None, visible=None, **kwargs):
        """Specify or change the data associated to particular template
        fields.
        
        Actual data upload on the GPU will occur during the rendering process, 
        in `paintGL`. It is just recorded here for later use.
        
        Arguments:
          * dataset=None: the relevant dataset. By default, the first one
            that has been created in `initialize`.
          * **kwargs: keyword arguments as `template_field_name: value` pairs.
        
        """
        if dataset is None:
            dataset = self.datasets[0]
        if visible is not None:
            dataset["visible"] = visible
        # this case happens during `create_dataset`: we just update the dataset
        # with the data so that it can be handled later
        if not self.is_initialized:
            dataset["datakwargs"].update(**kwargs)
        # this case happens after initialization, we update the data loader 
        # with the new data, no data transfer happens (it happens in 
        # `dataloader.upload_data` called in `paintGL`).
        else:
            dataset["loader"].set_data(**kwargs)
 
    # Methods related to DefaultTemplate
    # --------------------------------------
    def transform_view(self):
        """Change uniform variables to implement interactive navigation."""
        tx, ty = self.interaction_manager.get_translation()
        sx, sy = self.interaction_manager.get_scaling()
        scale = (np.float32(sx), np.float32(sy))
        translation = (np.float32(tx), np.float32(ty))
        for dataset in self.datasets:
            if not dataset["template"].is_static:
                self.set_data(dataset=dataset, 
                        scale=scale, translation=translation)
    
    def set_viewport(self, viewport, window_size):
        """Specify the viewport and the window size by changing the
        corresponding uniform values in all datasets."""
        for dataset in self.datasets:
            self.set_data(dataset=dataset, viewport=viewport,
                          window_size=window_size)
 
    def update_fps(self, fps):
        """Update the FPS in the corresponding text dataset."""
        self.set_data(dataset=self.ds_fps, text="FPS: %03d" % fps)
 
 
    # Rendering methods
    # -----------------
    def paint_dataset(self, dataset): #, **buffers_activations):
        """Paint a dataset.
        
        Arguments:
          * dataset: the dataset object, returned by `create_dataset` method.
          
        """
        primitive_type = dataset.get("primitive_type", PrimitiveType.Points)
        gl_primitive_type = GL_PRIMITIVE_TYPE_CONVERTER[primitive_type]
        dl = dataset["loader"]
        subdata_bounds = dl.subdata_bounds
        
        # activate shaders for this dataset
        dl.activate_shaders()
        
        # update invalidated data
        dl.upload_data()
        
        # go through all slices
        for slice_index in xrange(dl.slices_count):
            # get slice bounds
            slice_bounds = subdata_bounds[slice_index]
            
            # activate buffers
            for name, buffer in dl.attributes.iteritems():
                location = buffer["location"]
                ndim = buffer["ndim"]
                vbo, pos, size = buffer["vbos"][slice_index]
                activate_buffer(vbo, location, ndim) #, do_activate)

            # activate textures
            for name, texture in dl.textures.iteritems():
                textype = getattr(gl, "GL_TEXTURE_%dD" % texture["ndim"])
                gl.glBindTexture(textype, texture["location"])
                tex = texture["location"]-1
                # gl.glActiveTexture(gl.GL_TEXTURE0 + tex);
                 
            # just use a part of the buffer is bounds has 2 elements
            if len(slice_bounds) == 2:
                gl.glDrawArrays(gl_primitive_type, slice_bounds[0], slice_bounds[1] - slice_bounds[0])
            # use the Multi version of glDrawArrays for painting separate
            # objects in a single OpenGL call (most efficient)
            else:
                first = slice_bounds[:-1]
                count = np.diff(slice_bounds)
                primcount = len(slice_bounds) - 1
                gl.glMultiDrawArrays(gl_primitive_type, first, count, primcount)
        
        # deactivate shaders for this dataset
        dl.deactivate_shaders()
    
    def paint_all(self):
        """Render everything on the screen.
        
        This method is called by paintGL().
        
        """
        # transform the view for interactive navigation by updating the
        # corresponding uniform values in all non-static datasets
        self.transform_view()
        
        # plot all visible datasets
        for dataset in self.datasets:
            if dataset.get("visible", True):
                self.paint_dataset(dataset)
        
    def updateGL(self):
        """Call updateGL in the parent widget."""
        self.parent.updateGL()
        
        
    # Cleanup methods
    # ---------------
    def cleanup_buffer(self, buffer):
        """Clean up a buffer.
        
        Arguments:
          * buffer: a buffer object.
          
        """
        if "vbos" in buffer:
            bfs = [b[0] for b in buffer["vbos"]]
            gl.glDeleteBuffers(len(bfs), bfs)
    
    def cleanup_dataset(self, dataset):
        """Cleanup the dataset by deleting the associated shader program.
        
        Arguments:
          * dataset: the dataset to clean up.
        
        """
        program = dataset["loader"].shaders_program
        try:
            gl.glDeleteProgram(program)
        except Exception as e:
            log_info("error when deleting shader program")
        for buffer in dataset["loader"].attributes.itervalues():
            self.cleanup_buffer(buffer)
        
    def cleanup(self):
        """Cleanup all datasets."""
        for dataset in self.datasets:
            self.cleanup_dataset(dataset)
        
        
    # Methods to be overriden
    # -----------------------
    def initialize(self):
        """Initialize the data. To be overriden.

        This method can make calls to `create_dataset` and `set_data` methods.
        
        """
        pass
