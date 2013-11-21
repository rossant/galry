import numpy as np
from galry import *

class MyPaintManager(PlotPaintManager):
    def initialize(self):
        x = np.linspace(-1., 1., 1000)
        y = np.random.randn(1000)
        self.add_visual(PlotVisual, x=x, y=y)

class MyWidget(GalryWidget):
    def initialize(self):
        self.set_bindings(PlotBindings)
        self.set_companion_classes(
            paint_manager=MyPaintManager,
            interaction_manager=PlotInteractionManager,)
        self.initialize_companion_classes()

class Window(QtGui.QWidget):
    def __init__(self):
        super(Window, self).__init__()
        self.initUI()
        
    def initUI(self):
        vbox = QtGui.QVBoxLayout()
        vbox.addWidget(MyWidget())
        vbox.addWidget(MyWidget())
        self.setLayout(vbox)    
        
        self.setGeometry(300, 300, 600, 600)  
        self.show()
        
show_window(Window)
