import sys
import inspect
import os
import numpy as np
import time
import timeit
import collections
import subprocess
from qtools.qtpy import QtCore, QtGui
from qtools.utils import get_application, show_window
from functools import wraps
from galry import log_debug, log_info, log_warn
from collections import OrderedDict as ordict

# try importing numexpr
try:
    import numexpr
except:
    numexpr = None
    
__all__ = [
    'get_application',
    'get_intermediate_classes',
    'show_window',
    'run_all_scripts',
    'enforce_dtype',
    'FpsCounter',
    'ordict',
]
    

def hsv_to_rgb(hsv):
    """
    convert hsv values in a numpy array to rgb values
    both input and output arrays have shape (M,N,3)
    """
    h = hsv[:, :, 0]
    s = hsv[:, :, 1]
    v = hsv[:, :, 2]

    r = np.empty_like(h)
    g = np.empty_like(h)
    b = np.empty_like(h)

    i = (h * 6.0).astype(np.int)
    f = (h * 6.0) - i
    p = v * (1.0 - s)
    q = v * (1.0 - s * f)
    t = v * (1.0 - s * (1.0 - f))

    idx = i % 6 == 0
    r[idx] = v[idx]
    g[idx] = t[idx]
    b[idx] = p[idx]

    idx = i == 1
    r[idx] = q[idx]
    g[idx] = v[idx]
    b[idx] = p[idx]

    idx = i == 2
    r[idx] = p[idx]
    g[idx] = v[idx]
    b[idx] = t[idx]

    idx = i == 3
    r[idx] = p[idx]
    g[idx] = q[idx]
    b[idx] = v[idx]

    idx = i == 4
    r[idx] = t[idx]
    g[idx] = p[idx]
    b[idx] = v[idx]

    idx = i == 5
    r[idx] = v[idx]
    g[idx] = p[idx]
    b[idx] = q[idx]

    idx = s == 0
    r[idx] = v[idx]
    g[idx] = v[idx]
    b[idx] = v[idx]

    rgb = np.empty_like(hsv)
    rgb[:, :, 0] = r
    rgb[:, :, 1] = g
    rgb[:, :, 2] = b
    return rgb
    
def get_intermediate_classes(cls, baseclass):
    """Return all intermediate classes in the OO hierarchy between a base 
    class and a child class."""
    classes = inspect.getmro(cls)
    classes = [c for c in classes if issubclass(c, baseclass)]
    return classes
     
def run_all_scripts(dir=".", autodestruct=True, condition=None, ignore=[]):
    """Run all scripts successively."""
    if condition is None:
        condition = lambda file: file.endswith(".py") and not file.startswith("_")
    os.chdir(dir)
    files = sorted([file for file in os.listdir(dir) if condition(file)])
    for file in files:
        if file in ignore:
            continue
        print "Running %s..." % file
        args = ["python", file]
        if autodestruct:
            args += ["autodestruct"]
        subprocess.call(args)
        print "Done!"
        print

def enforce_dtype(arr, dtype, msg=""):
    """Force the dtype of a Numpy array."""
    if isinstance(arr, np.ndarray):
        if arr.dtype is not np.dtype(dtype):
            log_debug("enforcing dtype for array %s %s" % (str(arr.dtype), msg))
            return np.array(arr, dtype)
    return arr
    
def memoize(func):
    """Decorator for memoizing a function."""
    cache = {}
    @wraps(func)
    def wrap(*args):
        if args not in cache:
            cache[args] = func(*args)
        return cache[args]
    return wrap
    
def nid(x):
    """Return the address of an array data, used to check whether two arrays
    refer to the same data in memory."""
    return x.__array_interface__['data'][0]
    
class FpsCounter(object):
    """Count FPS."""
    # memory for the FPS counter
    maxlen = 10
    
    def __init__(self, maxlen=None):
        if maxlen is None:
            maxlen = self.maxlen
        self.times = collections.deque(maxlen=maxlen)
        self.fps = 0.
        self.delta = 0.
        
    def tick(self):
        """Record the current time stamp.
        
        To be called by paintGL().
        
        """
        self.times.append(timeit.default_timer())
        
    def get_fps(self):
        """Return the current FPS."""
        if len(self.times) >= 2:
            dif = np.diff(self.times)
            fps = 1. / dif.min()
            # if the FPS crosses 500, do not update it
            if fps <= 500:
                self.fps = fps
            return self.fps
        else:
            return 0.
            
