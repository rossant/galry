import numpy as np

__all__ = ['DataNormalizer']

class DataNormalizer(object):
    """Handles normalizing data so that it fits the fixed [-1,1]^2 viewport."""
    def __init__(self, data):
        self.data = data
    
    def normalize(self, initial_viewbox=None):
        """Normalize data given the initial view box.
        
        This function also defines the four following methods:
          * `(un)normalize_[x|y]`: normalize or un-normalize in the x or y
            dimension. Un-normalization can be useful for e.g. retrieving the
            original coordinates of a point in the window.
        
        Arguments:
          * initial_viewbox=None: the initial view box is a 4-tuple
            (x0, y0, x1, y1) describing the initial view of the data and
            defining the normalization. By default, it is the bounding box of the
            data (min/max x/y). x0 and/or y0 can be None, meaning no
            normalization for that dimension.
        
        Returns:
          * normalized_data: the normalized data.
        
        """
        x, y = self.data[:,0], self.data[:,1]
        if initial_viewbox is None:
            initial_viewbox = (None, None, None, None)
        dx0, dy0, dx1, dy1 = initial_viewbox
        
        # default: replace None by min/max
        if dx0 is None:
            dx0 = x.min()
        if dy0 is None:
            dy0 = y.min()
        if dx1 is None:
            dx1 = x.max()
        if dy1 is None:
            dy1 = y.max()
        
        if dx0 == dx1:
            dx0 -= .5
            dx1 += .5
        if dy0 == dy1:
            dy0 -= .5
            dy1 += .5        
        if dx0 is None:
            self.normalize_x = self.unnormalize_x = lambda X: X
        else:
            self.normalize_x = lambda X: -1+2*(X-dx0)/(dx1-dx0)
            self.unnormalize_x = lambda X: dx0 + (dx1 - dx0) * (1+X)/2.
        if dy0 is None:
            self.normalize_y = self.unnormalize_y = lambda Y: Y
        else:
            self.normalize_y = lambda Y: -1+2*(Y-dy0)/(dy1-dy0)
            self.unnormalize_y = lambda Y: dy0 + (dy1 - dy0) * (1+Y)/2.
        data_normalized = np.empty(self.data.shape, dtype=self.data.dtype)
        data_normalized[:,0] = self.normalize_x(x)
        data_normalized[:,1] = self.normalize_y(y)
        return data_normalized
    