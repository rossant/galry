"""Galry unit tests.

Every test shows a GalryWidget with a white square (non filled) and a black
background. Every test uses a different technique to show the same picture
on the screen. Then, the output image is automatically saved as a PNG file and
it is then compared to the ground truth.

"""
import unittest
import os
import re
from galry import *
from matplotlib.pyplot import imread

# reference image
REFIMG = imread("autosave/_REF.png")

class GalryTest(unittest.TestCase):
    """Base class for the tests. Child classes should call `self.show` with
    the same keyword arguments as those of `show_basic_window`.
    The window will be open for a short time and the image will be recorded
    for automatic comparison with the ground truth."""
        
    def classname(self):
        """Return the class name."""
        return self.__class__.__name__
        
    def filename(self):
        """Return the filename of the output image, depending on this class
        name."""
        return "autosave/%s.png" % self.classname()
        
    def reference_image(self):
        filename = "autosave/%s.ref.png" % self.classname()
        if os.path.exists(filename):
            return imread(filename)
        else:
            return REFIMG
        
    def _show(self, **kwargs):
        """Show the window during a short period of time, and save the output
        image."""
        return show_basic_window(autosave=self.filename(),
                autodestruct=100., **kwargs)

    kwargs = {}
    def show(self, **kwargs):
        """Create a window with the given parameters."""
        self.kwargs = kwargs
        
    def test(self):
        """Launch the specified window and check that the output image is the
        same as the reference image."""
        if self.classname() != 'GalryTest':
            self.start()
            self._show(**self.kwargs)
            # make sure the output image is the same as the reference image
            img = imread(self.filename())
            self.assertTrue(np.allclose(img, self.reference_image()))
        
    def start(self):
        """To be overriden. Make a call to self.show."""
        
                
def all_tests(folder=None):
    if folder is None:
        folder = os.path.dirname(os.path.realpath(__file__))
    suites = unittest.TestLoader().discover(folder, pattern='*_test.py')
    allsuites = unittest.TestSuite(suites)
    return allsuites

def test():
    unittest.main(defaultTest='all_tests')

if __name__ == '__main__':
    test()
