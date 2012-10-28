import sys
import time
import numpy as np
import OpenGL.GL as gl
import OpenGL.arrays.vbo as glvbo
import OpenGL.GLUT as glut
from tools import enum, memoize, enforce_dtype
# from default_shaders import DEFAULT_SHADERS
# from shaders import ShadersCreator
import ctypes
from debugtools import log_debug, log_info, log_warn
import templates as tpl
from dataloader import DataLoader, NP_GL_TYPE_CONVERTER, activate_buffer
from primitives import PrimitiveType, GL_PRIMITIVE_TYPE_CONVERTER

__all__ = ['PaintManager']


    
# PaintManager class
# ------------------                   
class PaintManager(object):
    """Defines what to render in the widget."""
    
    # Background color.
    bgcolor = (0., 0., 0., 0.)
    
    # Initialization methods
    # ----------------------
    def __init__(self):
        # current absolute translation offset, used because glTranslate is
        # relative to the current position
        self.current_offset = (0, 0)
        
        # list of datasets
        self.datasets = []

        # list of text strings to display
        # self.texts = []
        # self.permanent_overlays = []
        # self.transient_overlays = []
        
        self.is_initialized = False

    def initialize_default(self):
        if self.parent.display_fps:
            text = "FPS: 000"
            self.ds_fps = self.create_dataset(
                size=len(text),
                template_class=tpl.TextTemplate,
                position=(-.82, .92),
                fontsize=18,
                color=(1.,1.,1.,1.),
                is_static=True,
                text=text)

    def initialize_gpu(self):
        for dataset in self.datasets:
            dataset["loader"].compile_shaders()
            for variable in ["attribute", "uniform", "texture"]: 
                names = getattr(dataset["loader"], variable + "s").keys()
                dataset["loader"].upload_variables(*names)
        self.is_initialized = True
 
        
    # Data creation methods
    # ---------------------
    def create_dataset(self,
                       template_class=None,
                       size=None,
                       # rendering options
                       bounds=None,
                       primitive_type=None,
                       default_color=None,
                       **kwargs):
        """Create a dataset.
        
        A dataset is the combination of:
          * a set of `N` points,
          * a vertex shader and fragment shader source codes,
          * any number of buffers, each buffer having a name and corresponding 
            to an actual data array,
          * a set of textures (TODO: only one texture support is implemented 
            currently).
        
        All the buffers are processed on the GPU through vertex and fragment
        shaders. The role of shaders is to transform data contained in these
        buffers into 2D or 3D colored vertices on the screen.
        The vertex shader generates the positions of the vertices.
        The fragment shader generates the colors of the vertices.
        
        Default shaders are provided in the helper painting methods.
        Custom shaders can be specified if needed. That's an advanced 
        and extremely powerful feature. One needs to know the OpenGL 
        programmable pipeline and the GLSL language in order to write their
        own shaders.
        
        Arguments:
          * size: the size of the dataset, i.e. the number of points.
          * bounds=None: the data bounds separating the individual objects to
            display. It should be an array of int32 with all bound indices.
            The first index must be 0, the last one is `size`. Every index
            gives the position of the first point in the current primitive.
            The default (`None`) is just `[0, size]`.
          * primitive_type=None: a member of the `PrimitiveType` enumeration
            with the primitive type to render for this dataset. By default,
            it is `PrimitiveType.Points`.
          * color=None: the default color of the rendered primitives. It is
            yellow by default. This value may not be used depending on the
            specific fragment shader.
          * vertex_shader=None: the source code of the vertex shader.
          * fragment_shader=None: the source code of the fragment shader.
          * is_static=False: whether the rendered objects should be transformed
            by the interactive navigation or stay at a fixed position in the
            window.
          * **uniforms: keyword arguments of uniform variables, with their 
            initial values.
          
        Returns:
          * dataset: a dictionary containing all the information about
            the dataset, and that can be used in the methods of `PaintManager`.
        
        """
        
        if not template_class:
            template_class = tpl.DefaultTemplate
            
        template = template_class(size=size)
        if self.parent.constrain_ratio:
            kwargs["constrain_ratio"] = True
        template.initialize(**kwargs)
        size = template.size
        
        # we pass the default color to the template, only if it is not None
        template.set_default_color(default_color)
        
        if primitive_type is None:
            # if primitive_type is specified in create_dataset, we take it.
            # otherwise, we take the one that may have been defined in the
            # template (in template.set_rendering_options, called in
            # initialize)
            # finally, we fallback on Points
            primitive_type = getattr(template, "primitive_type",
                    PrimitiveType.Points)
        
        if bounds is None:
            # if bounds is specified, we take it
            # otherwise, we take the one that may have been defined in the
            # template (in template.set_rendering_options, called in
            # initialize)
            # finally, we fallback on the default bounds
            bounds = getattr(template, "bounds", [0, size])
        bounds = np.array(bounds, np.int32)
        
        template.finalize()
        
        dataset = {}
        dataset["size"] = size
        dataset["template"] = template
        
        dataset["primitive_type"] = primitive_type
        
        dataset["loader"] = DataLoader(size, template=template, bounds=bounds)        
        # default data
        self.set_data(dataset=dataset, **template.default_data)
        
        self.datasets.append(dataset)
        return dataset

    def set_data(self, dataset=None, **kwargs):
        if dataset is None:
            dataset = self.datasets[0]
        vars_to_update = dataset["loader"].set_data(**kwargs)
        if self.is_initialized:
            dataset["loader"].upload_variables(*vars_to_update)
    
 
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
        for dataset in self.datasets:
            self.set_data(dataset=dataset, viewport=viewport,
                            window_size=window_size)
 
    def update_fps(self, fps):
        self.set_data(dataset=self.ds_fps, text="FPS: %03d" % fps)
 
    # Overlay methods
    # ---------------
    # def add_transient_overlay(self, name, *args, **kwargs):
        # """Add transient overlay.
        
        # This function adds an overlay in only one rendering pass.
        # It should be called during the life of the widget.
        
        # Arguments:
          # * name: the name of the overlay. The engine will call the 
           # `paint_[name]` method at the next rendering pass.
          # * static=False: whether this overlay should have a fixed position
            # on the screen or not.
          # * *args, **kwargs: arguments of that paint method.
        
        # """
        # self.transient_overlays.append((name, args, kwargs))
    
    # def add_permanent_overlay(self, name, *args, **kwargs):
        # """Add permanent overlay.
        
        # This function adds an overlay in all rendering passes.
        # WARNING: it should only be called at initialization, otherwise
        # an infinite number of permanent overlays will be created.
        
        # Arguments:
          # * name: the name of the overlay. The engine will call the 
           # `paint_[name]` method in all rendering passes.
          # * static=False: whether this overlay should have a fixed position
            # on the screen or not.
          # * *args, **kwargs: arguments of that paint method.
        
        # """
        # self.permanent_overlays.append((name, args, kwargs))
    
    # def add_text(self, text, position=(0,0), color=None):
        # """Add text as a permanent overlay.
        
        # WARNING: To be called at initialization time only.
        
        # Arguments:
          # * text: a string, or a function returning a string (useful when the
            # text needs to be dynamic).
          # * position=(0,0): the position of the text in the window relative 
            # coordinates (in [-1,1]^2).
          # * color=None: the color of the text, yellow by default.
        
        # """
        # self.add_permanent_overlay("text", text, position=position, color=color)
    
    
    # Rendering methods
    # -----------------
    def paint_dataset(self, dataset, primitive_type=None, #color=None,
                      **buffers_activations):
        """Paint a dataset.
        
        Arguments:
          * dataset: the dataset object, returned by `create_dataset` method.
          * primitive_type=None: a PrimitiveType enum value. By default, 
            the value specified in the dataset creation is used.
          * color=None: the color of the primitives. If None, the color
            specified in the buffer will be used.
          **buffers_activations: for each name, whether to activate or not
            this buffer. It is True by default for all buffers in the dataset.
          
        """
        if primitive_type is None:
            primitive_type = dataset.get("primitive_type", PrimitiveType.Points)
        # if color is None:
        # color = dataset["color"]
        gl_primitive_type = GL_PRIMITIVE_TYPE_CONVERTER[primitive_type]
        
        dl = dataset["loader"]
        
        subdata_bounds = dl.subdata_bounds
        
        # by default, choose to activate non specified buffers
        for name, buffer in dl.attributes.iteritems():
            if name not in buffers_activations:
                buffers_activations[name] = True
        
        # activate shaders for this dataset
        dl.activate_shaders()
        
        # update invalidated uniforms
        dl.upload_invalidated_uniform_data()
        
        # go through all slices
        for slice_index in xrange(dl.slices_count):
            # get slice bounds
            slice_bounds = subdata_bounds[slice_index]
            
            # activate or deactivate buffers
            for name, do_activate in buffers_activations.iteritems():
                # self.activate_buffer(dataset, name, slice_index, do_activate)
                
                buffer = dataset["loader"].attributes[name]
                location = buffer["location"]
                ndim = buffer["ndim"]
                vbo, pos, size = buffer["vbos"][slice_index]
                
                activate_buffer(vbo, location, ndim, do_activate)
                
                
                
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
        
        # activate textures
        for name, texture in dl.textures.iteritems():
            textype = getattr(gl, "GL_TEXTURE_%dD" % texture["ndim"])
            gl.glBindTexture(textype, texture["location"])
            # gl.glActiveTexture(gl.GL_TEXTURE0 + 0);
        
        # deactivate shaders for this dataset
        dl.deactivate_shaders()
    
    # def paint_overlays(self, static=True):
        # """Paint permanent and transient overlays.
        
        # Arguments:
          # * static=True: whether to paint static or non-static overlays.
        
        # """
        # for overlay in self.permanent_overlays + self.transient_overlays:
            # name, args, kwargs = overlay
            # static_overlay = kwargs.get("static", True)
            # if static_overlay == static:
                # getattr(self, "paint_" + name)(*args, **kwargs)    
       
    # def paint_text(self, text, position, color=None):
        # """Paint a text.
        
        # Arguments:
          # * text: a string with the text to paint.
          # * position: a 2-tuple with the coordinates of the text.
          # * color: the color of the text as a 3- or 4- tuple.
          
        # """
        # # TODO: implement this in textures?
        # # advantages:
        # #   * simpler for handling interactive navigation
        # #   * more portable, more flexible
        # #   * no need to mess around with freeglut
        # if color is not None:
            # gl.glColor(*color)
        # gl.glRasterPos2f(*position)
        # if callable(text):
            # text = text()
        # try:
            # glut.glutBitmapString(glut.GLUT_BITMAP_HELVETICA_12, text)
        # except Exception as e:
            # log_warn("an error occurred when display text '%s': %s. You probably \
# need to install freeglut." % (text, e.message))
        
    # def paint_rectangle(self, points, color=None):
        # """Paint a rectangle.
        
        # Arguments:
          # * points: the rectangle coordinates as `(x0, y0, x1, y1)`.
          # * color=None: the rectangle fill color as a 3- or 4- tuple.
        
        # """
        # if color is not None:
            # gl.glColor(*color)
        # gl.glRectf(*points)
    
    def paint_all(self):
        """Render everything on the screen.
        
        This method is called by paintGL().
        
        """
        # Interactive transformation ON
        # -----------------------------
        self.transform_view()
        
        # plot all datasets
        for dataset in self.datasets:
            self.paint_dataset(dataset)
        
        # paint non static overlays
        # self.paint_overlays(static=False)
        
        # Interactive transformation OFF
        # ------------------------------
        # cancel the transformation (static position after this line)
        # gl.glLoadIdentity()
        
        # paint static overlays
        # self.paint_overlays(static=True)
        
        # remove transient overlays
        # self.transient_overlays = []
        
    def updateGL(self):
        """Update rendering."""
        self.parent.updateGL()
        
        
    # Cleanup methods
    # ---------------
    def cleanup_buffer(self, buffer):
        """Clean up a buffer.
        
        Arguments:
          * buffer: a buffer object.
          
        """
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
            log_warn("error when deleting shader program")
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

        This method can make calls to `create_dataset` and `add_*` methods.
        
        """
        pass
