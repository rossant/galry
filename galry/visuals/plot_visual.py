import numpy as np
from galry import get_color, get_next_color
from visual import Visual

__all__ = ['process_coordinates', 'PlotVisual']

def process_coordinates(x=None, y=None, thickness=None):
    # handle the case where x is defined and not y: create x
    if y is None and x is not None:
        if x.ndim == 1:
            x = x.reshape((1, -1))
        nplots, nsamples = x.shape
        y = x
        x = np.tile(np.linspace(0., 1., nsamples).reshape((1, -1)), (nplots, 1))
        
    # convert into arrays
    x = np.array(x, dtype=np.float32)#.squeeze()
    y = np.array(y, dtype=np.float32)#.squeeze()
    
    # x and y should have the same shape
    assert x.shape == y.shape
    
    # enforce 2D for arrays
    if x.ndim == 1:
        x = x.reshape((1, -1))
        y = y.reshape((1, -1))
    
    # create the position matrix
    position = np.empty((x.size, 2), dtype=np.float32)
    position[:, 0] = x.ravel()
    position[:, 1] = y.ravel()
    
    
    return position, x.shape
    

class PlotVisual(Visual):
    def initialize(self, x=None, y=None, color=None, point_size=1.0,
            position=None, nprimitives=None, index=None,
            color_array_index=None, thickness=None,
            options=None, autocolor=None, autonormalizable=True):
            
        # if position is specified, it contains x and y as column vectors
        if position is not None:
            position = np.array(position, dtype=np.float32)
            if thickness:
                shape = (2 * position.shape[0], 1)
            else:
                shape = (1, position.shape[0])
        else:
            position, shape = process_coordinates(x=x, y=y)
            if thickness:
                shape = (shape[0], 2 * shape[1])
        
        
        # register the size of the data
        self.size = np.prod(shape)
        
        # there is one plot per row
        if not nprimitives:
            nprimitives = shape[0]
            nsamples = shape[1]
        else:
            nsamples = self.size // nprimitives
        
        
        # handle thickness
        if thickness and position.shape[0] >= 2:
            w = thickness
            n = self.size
            X = position
            Y = np.zeros((n, 2))
            u = np.zeros((n/2, 2))
            X2 = np.vstack((X, 2*X[-1,:]-X[-2,:]))
            u[:,0] = -np.diff(X2[:,1])
            u[:,1] = np.diff(X2[:,0])
            r = (u[:,0] ** 2 + u[:,1] ** 2) ** .5
            rm = r.mean()
            r[r == 0.] = rm
            # print u
            # print r
            # ind = np.nonzero(r == 0.)[0]
            # print ind, ind-1
            # r[ind] = r[ind - 1]
            u[:,0] /= r
            u[:,1] /= r
            Y[::2,:] = X - w * u
            Y[1::2,:] = X + w * u
            position = Y
            x = Y[:,0]
            y = Y[:,1]
            # print x
            # print y
            self.primitive_type = 'TRIANGLE_STRIP'
            
            
        # register the bounds
        if nsamples <= 1:
            self.bounds = [0, self.size]
        else:
            self.bounds = np.arange(0, self.size + 1, nsamples)
        
        # normalize position
        # if viewbox:
            # self.add_normalizer('position', viewbox)
        
        # by default, use the default color
        if color is None:
            if nprimitives <= 1:
                color = self.default_color
        
        # automatic color with color map
        if autocolor is not None:
            if nprimitives <= 1:
                color = get_next_color(autocolor)
            else:
                color = [get_next_color(i + autocolor) for i in xrange(nprimitives)]
            
            
        # # handle the case where the color is a string where each character
        # # is a color (eg. 'ry')
        # if isinstance(color, basestring):
            # color = list(color)
        color = get_color(color)
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
        self.add_attribute("position", ndim=2, data=position, 
            autonormalizable=autonormalizable)
        
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
        
