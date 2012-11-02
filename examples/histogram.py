from galry import *
import numpy as np
import numpy.random as rdn

def get_histogram_points(hist):
    """Tesselates histograms.
    
    Arguments:
      * hist: a N x Nsamples array, where each line contains an histogram.
      
    Returns:
      * X, Y: two N x (5 * Nsamples + 1) arrays with the coordinates of the
        histograms, to be rendered as a TriangleStrip.
      
    """
    n, nsamples = hist.shape
    dx = 2. / nsamples
    
    x0 = -1 + dx * np.arange(nsamples)
    
    x = np.zeros((n, 5 * nsamples + 1))
    y = -np.ones((n, 5 * nsamples + 1))
    
    x[:,0:-1:5] = x0
    x[:,1::5] = x0
    x[:,2::5] = x0 + dx
    x[:,3::5] = x0
    x[:,4::5] = x0 + dx
    x[:,-1] = 1
    
    y[:,1::5] = hist
    y[:,2::5] = hist
    
    return x, y


class HistogramPaintManager(PaintManager):
    def initialize(self):
        # random histogram values
        values = rdn.rand(1, 50)
        # compute histogram points
        X, Y = get_histogram_points(values)
        position = np.hstack((X.reshape((-1, 1)),
            Y.reshape((-1, 1))))
        # add the bar plot
        self.create_dataset(PlotTemplate, nsamples=5,
            primitive_type=PrimitiveType.TriangleStrip,
            position=position)

if __name__ == '__main__':
    # create window
    window = show_basic_window(paint_manager=HistogramPaintManager)
