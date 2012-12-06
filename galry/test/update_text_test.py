import unittest
from galry import *
from test import GalryTest

class PM(PaintManager):
    def initialize(self):
        # test buffer updating with different sizes
        self.add_visual(TextVisual, text="short")
        self.set_data(coordinates=(0., .5), text="long text!")
        
class UpdateTextTest(GalryTest):
    def test(self):
        window = self.show(paint_manager=PM)

if __name__ == '__main__':
    unittest.main()
    # show_basic_window(paint_manager=PM)
