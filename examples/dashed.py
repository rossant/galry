from galry import *
import numpy as np

class SinusPaintManager(PaintManager):
    def initialize(self):
        x = np.linspace(-1., 1., 1000)
        y = 0.5 * np.sin(20 * x)

        color = np.array(get_color(['w', 'k']))
        index = np.zeros(len(x))
        index[::2] = 1
        
        self.add_visual(PlotVisual,
            x=x, y=y, color_array_index=index, color=color,)

if __name__ == '__main__':
    # create window
    window = show_basic_window(paint_manager=SinusPaintManager)
    