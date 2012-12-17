from plot_visual import PlotVisual
import numpy as np

__all__ = ['BarVisual']

def get_histogram_points(hist):
    """Tesselates histograms.
    
    Arguments:
      * hist: a N x Nsamples array, where each line contains an histogram.
      
    Returns:
      * X, Y: two N x (5 * Nsamples + 1) arrays with the coordinates of the
        histograms, to be rendered as a TriangleStrip.
      
    """
    n, nsamples = hist.shape
    dx = 1. / nsamples
    
    x0 = dx * np.arange(nsamples)
    
    x = np.zeros((n, 5 * nsamples + 1))
    y = np.zeros((n, 5 * nsamples + 1))
    
    x[:,0:-1:5] = x0
    x[:,1::5] = x0
    x[:,2::5] = x0 + dx
    x[:,3::5] = x0
    x[:,4::5] = x0 + dx
    x[:,-1] = 1
    
    y[:,1::5] = hist
    y[:,2::5] = hist
    
    return x, y


class BarVisual(PlotVisual):
    def initialize(self, values=None, offset=None, **kwargs):
    
        if values.ndim == 1:
            values = values.reshape((1, -1))
            
        # compute histogram points
        x, y = get_histogram_points(values)
        
        if offset is not None:
            x += offset[:,0].reshape((-1, 1))
            y += offset[:,1].reshape((-1, 1))
        
        # add the bar plot
        super(BarVisual, self).initialize(x=x, y=y, **kwargs)

        self.primitive_type='TRIANGLE_STRIP'