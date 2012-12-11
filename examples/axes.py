from galry import *
import numpy as np

class PM(PaintManager):
    def initialize(self):
        self.add_visual(PlotVisual, position=np.random.randn(100000, 2) * .2,
            primitive_type='POINTS')
            
        self.add_visual(GridVisual)
        
class IM(InteractionManager):
    def initialize(self):
        self.add_processor(GridEventProcessor, name='ticks')

show_basic_window(paint_manager=PM, 
    interaction_manager=IM)

