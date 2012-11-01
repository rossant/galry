from ..galrywidget import GalryWidget, show_basic_window
from ..paintmanager import PaintManager, PrimitiveType
from ..templates import PlotTemplate
import numpy as np
from colors import get_color

class PlotObject(object):
    def __init__(self, **kwargs):
        """Initialize a Plot object. The keywoard arguments will be passed
        to PaintManager.create_dataset."""
        self.kwargs = kwargs
        
    def set_data(self, **kwargs):
        """Keyword arguments for set_data(dataset)."""
        self.data = kwargs
        
        

class PlotPaintManager(PaintManager):
    def __init__(self, **kwargs):
        super(PlotPaintManager, self).__init__(**kwargs)
        self.objects = []
    
    def add_object(self, object):
        self.objects.append(object)
    
    def add_plot(self, X, Y, color=None, primitive_type=None):
        
        assert X.ndim == 2
        assert X.shape == Y.shape
        
        nprimitives, nsamples = X.shape
        size = X.size
        
        position = np.empty((size, 2), dtype=np.float32)
        position[:,0] = X.ravel()
        position[:,1] = Y.ravel()
        
        if primitive_type is None:
            primitive_type = PrimitiveType.LineStrip
        
        # Handle the case where color is a list of RGB(A) values with a single
        # color
        if type(color) is list and color:
            if (type(color[0]) == float) and (3 <= len(color) <= 4):
                color = tuple(color)
        
        # empty color => None
        if not color:
            color = None
        
        if type(color) == str:
            color = get_color(color)
            
        if color is None:
            colors_ndim = 4
            single_color = True
            color = get_color('y')
        elif type(color) == tuple:
            colors_ndim = len(color)
            single_color = True
        elif type(color) == list:
            assert len(color) == nprimitives
            color = get_color(color)
            colors_ndim = len(color[0])
            single_color = False
            
        print color
        
        obj = PlotObject(template_class=PlotTemplate,
                         size=size,
                         primitive_type=primitive_type,
                         colors_ndim=colors_ndim,
                         single_color=single_color,
                         nprimitives=nprimitives,
                         nsamples=nsamples)

        obj.set_data(position=position, color=color)
        self.add_object(obj)

    def initialize(self):
        for object in self.objects:
            ds = self.create_dataset(**object.kwargs)
            self.set_data(dataset=ds, **object.data)
    
    
    
class PlotWidget(GalryWidget):
    def initialize(self):
        self.set_companion_classes(paint_manager=PlotPaintManager,
            )
    
    
    
    