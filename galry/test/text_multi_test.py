import unittest
from galry import *
from test import GalryTest
import numpy as np

class PM(PaintManager):
    def initialize(self):
        text = ["Hello", "world! :)"]
        self.add_visual(TextVisual, text=text,
            coordinates=[(0., 0.), (0., .5)])


class TextMultiTest(GalryTest):
    def test(self):
        self.show(paint_manager=PM)

if __name__ == '__main__':
    unittest.main()
    # show_basic_window(paint_manager=PM)
