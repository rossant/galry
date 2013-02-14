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

def get_image_path(filename=''):
    path = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(path, 'autosave/%s' % filename)

REFIMG = imread(get_image_path('_REF.png'))

# maximum accepted difference between the sums of the test and 
# reference images
TOLERANCE = 10

def erase_images():
    log_info("Erasing all non reference images.")
    # erase all non ref png at the beginning
    l = filter(lambda f: not(f.endswith('REF.png')),# and f != '_REF.png', 
        os.listdir(get_image_path()))
    [os.remove(get_image_path(f)) for f in l]

def compare_subimages(img1, img2):
    """Compare the sum of the values in the two images."""
    return np.abs(img1.sum() - img2.sum()) <= TOLERANCE
    
def compare_images(img1, img2):
    """Compare the sum of the values in the two images and in two
    quarter subimages in opposite corners."""
    n, m, k = img1.shape
    boo = compare_subimages(img1, img2)
    boo = boo and compare_subimages(img1[:n/2, :m/2, ...], img2[:n/2, :m/2, ...])
    boo = boo and compare_subimages(img1[n/2:, m/2:, ...], img2[n/2:, m/2:, ...])
    return boo
          
class GalryTest(unittest.TestCase):
    """Base class for the tests. Child classes should call `self.show` with
    the same keyword arguments as those of `show_basic_window`.
    The window will be open for a short time and the image will be recorded
    for automatic comparison with the ground truth."""
        
    # in milliseconds
    autodestruct = 100
    
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
        return get_image_path(self.classname() + '.png')
        
    def reference_image(self):
        filename = get_image_path(self.classname() + '.REF.png')
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
        boo = compare_images(img, self.reference_image())
        self.assertTrue(boo)
        return window

class MyTestSuite(unittest.TestSuite):
    def run(self, *args, **kwargs):
        erase_images()
        super(MyTestSuite, self).run(*args, **kwargs)

def all_tests(pattern=None, folder=None):
    if folder is None:
        folder = os.path.dirname(os.path.realpath(__file__))
    if pattern is None:
        pattern = '*_test.py'
    suites = unittest.TestLoader().discover(folder, pattern=pattern)
    allsuites = MyTestSuite(suites)
    return allsuites

def test(pattern=None, folder=None):
    # unittest.main(defaultTest='all_tests')
    unittest.TextTestRunner(verbosity=2).run(all_tests(folder=folder,
        pattern=pattern))

if __name__ == '__main__':
    test()
