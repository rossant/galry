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
        
    # in milliseconds
    autodestruct = 100
        
    # maximum accepted difference between the sums of the test and 
    # reference images
    tolerance = 10
    
    def log_header(self, s):
        s += '\n' + ('-' * (len(s) + 10))
        log_info(s)
        
    def setUp(self):
        self.log_header("Running test %s..." % self.classname())
        
    def tearDown(self):
        self.log_header("Test %s finished!" % self.classname())
        
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
                autodestruct=self.autodestruct, **kwargs)

    def show(self, **kwargs):
        """Create a window with the given parameters."""
        window = self._show(**kwargs)
        # make sure the output image is the same as the reference image
        img = imread(self.filename())
        n1, n2 = img.sum(), self.reference_image().sum()
        d = np.abs(n1 - n2)
        boo = d <= self.tolerance
        if not boo:
            log_warn(("Images sums differ by %.0f whereas the tolerance is " \
                + "%d") % (d, self.tolerance))
        self.assertTrue(boo)
        return window
            
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
