import numpy as np
from visual import Visual

class PlotVisual(Visual):
    def initialize(self, x=None, y=None, color=None, point_size=1.0,
            position=None, nprimitives=None, index=None,
            color_array_index=None):
            
        # if position is specified, it contains x and y as column vectors
        if position is not None:
            x, y = position.T
        
        # remove single-dimensional dimensions
        x = np.array(x, dtype=np.float32).squeeze()
        y = np.array(y, dtype=np.float32).squeeze()
        
        # x and y should have the same shape
        assert x.shape == y.shape
        
        # enforce 2D for arrays
        if x.ndim == 1:
            x = x.reshape((1, -1))
            y = y.reshape((1, -1))
        
        # register the size of the data
        self.size = x.size
        
        # there is one plot per row
        if not nprimitives:
            nprimitives = x.shape[0]
            nsamples = x.shape[1]
        else:
            nsamples = x.size // nprimitives
        
        # register the bounds
        if nsamples == 0:
            self.bounds = [0, 0]
        else:
            self.bounds = np.arange(0, self.size + 1, nsamples)
        
        # create the position matrix
        position = np.empty((self.size, 2), dtype=np.float32)
        position[:, 0] = x.ravel()
        position[:, 1] = y.ravel()

        # by default, use the default color
        if color is None:
            color = self.default_color
            
        # handle the case where there is a single color given as a list of
        # RGB components instead of a tuple
        if type(color) is list:
            if color and (type(color[0]) != tuple) and (3 <= len(color) <= 4):
                color = tuple(color)
            else:
                color = np.array(color)
        # first, initialize use_color_array to False except if
        # color_array_index is not None
        use_color_array = color_array_index is not None
        if isinstance(color, np.ndarray):
            colors_ndim = color.shape[1]
            # first case: one color per point
            if color.shape[0] == self.size:
                single_color = False
            # second case: use a color array so that each plot has a single
            # color, this saves memory since there is a single color in
            # memory for any plot
            else:
                use_color_array = True
                single_color = False
        elif type(color) is tuple:
            single_color = True
            colors_ndim = len(color)
        
        # set position attribute
        self.add_attribute("position", ndim=2, data=position)
        
        if index is not None:
            index = np.array(index)
            # self.size = len(index)
            self.add_index("index", data=index)
        
        # single color case: no need for a color buffer, just use default color
        if single_color and not use_color_array:
            self.add_uniform("color", ndim=colors_ndim, data=color)
            if colors_ndim == 3:
                self.add_fragment_main("""
            out_color = vec4(color, 1.0);
                """)
            elif colors_ndim == 4:
                self.add_fragment_main("""
            out_color = color;
                """)
        
        # multiple colors case: color attribute
        elif not use_color_array:
            self.add_attribute("color", ndim=colors_ndim, data=color)
            self.add_varying("varying_color", vartype="float", ndim=colors_ndim)
            
            self.add_vertex_main("""
            varying_color = color;
            """)
            
            if colors_ndim == 3:
                self.add_fragment_main("""
            out_color = vec4(varying_color, 1.0);
                """)
            elif colors_ndim == 4:
                self.add_fragment_main("""
            out_color = varying_color;
                """)
        
        # multiple colors, but with a color array to save memory
        elif use_color_array:
            if color_array_index is None:
                color_array_index = np.repeat(np.arange(nprimitives), nsamples)
            color_array_index = np.array(color_array_index)
                
            ncolors = color.shape[0]
            ncomponents = color.shape[1]
            color = color.reshape((1, ncolors, ncomponents))
            
            dx = 1. / ncolors
            offset = dx / 2.
            
            self.add_texture('colormap', ncomponents=ncomponents, ndim=1, data=color)
            self.add_attribute('index', ndim=1, vartype='int', data=color_array_index)
            self.add_varying('vindex', vartype='int', ndim=1)
            
            self.add_vertex_main("""
            vindex = index;
            """)
            
            self.add_fragment_main("""
            float coord = %.5f + vindex * %.5f;
            vec4 color = texture1D(colormap, coord);
            out_color = color;
            """ % (offset, dx))

        
        # add point size uniform (when it's not specified, there might be some
        # bugs where its value is obtained from other datasets...)
        self.add_uniform("point_size", data=point_size)
        self.add_vertex_main("""gl_PointSize = point_size;""")
        
