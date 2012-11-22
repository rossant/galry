import numpy as np
from visual import Visual


class PlotVisual(Visual):
    def initialize(self, x=None, y=None, color=None, point_size=1.0, position=None):
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
        nprimitives = x.shape[0]
        nsamples = x.shape[1]
        
        # register the bounds
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
        use_color_array = False
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
        
        # single color case: no need for a color buffer, just use default color
        if single_color:
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
            color_array_index = np.repeat(np.arange(nprimitives), nsamples)
            
            self.add_attribute("color_array_index", vartype="int", ndim=1,
                data=color_array_index)
                
            color_array_size = color.shape[0]
                
            self.add_uniform("color", vartype="float", ndim=colors_ndim,
                size=color_array_size, data=color)
            self.add_varying("varying_color", vartype="float", ndim=colors_ndim)
            
            self.add_vertex_main("""
        varying_color = color[int(color_array_index)];
            """)
            
            if colors_ndim == 3:
                self.add_fragment_main("""
            out_color = vec4(varying_color, 1.0);
                """)
            elif colors_ndim == 4:
                self.add_fragment_main("""
            out_color = varying_color;
                """)

        # add point size uniform (when it's not specified, there might be some
        # bugs where its value is obtained from other datasets...)
        self.add_uniform("point_size", data=point_size)
        self.add_vertex_main("""gl_PointSize = point_size;""")
                
        
if __name__ == '__main__':
    x = .2 * np.random.randn(10, 10000)
    y = .2 * np.random.randn(10, 10000)
    color = np.random.rand(10, 4)
    color[:,:2] += .2
    color[:, -1] = .1
    v = PlotVisual(x, y, color=color)
    d = v.get_dic()

    # print d['vertex_shader']
    # print d['fragment_shader']
    # import pprint
    # pprint.pprint(d)

    from glrenderer import show_scene, show_visual
    show_visual(d)



    