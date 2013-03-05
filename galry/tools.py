import sys
import inspect
import os
import numpy as np
import time
import timeit
import collections
import subprocess
from qtools.qtpy import QtCore, QtGui
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
    
def get_intermediate_classes(cls, baseclass):
    """Return all intermediate classes in the OO hierarchy between a base 
    class and a child class."""
    classes = inspect.getmro(cls)
    classes = [c for c in classes if issubclass(c, baseclass)]
    return classes
    
def get_application():
    """Get the current QApplication, or create a new one."""
    app_created = False
    app = QtCore.QCoreApplication.instance()
    if app is None:
        log_debug("creating a new QApplication in order to show the window")
        app = QtGui.QApplication(sys.argv)
        app_created = True
    return app, app_created
    
def show_window(window, **kwargs):
    """Create a QT window in Python, or interactively in IPython with QT GUI
    event loop integration:
    
        # in ~/.ipython/ipython_config.py
        c.TerminalIPythonApp.gui = 'qt'
        c.TerminalIPythonApp.pylab = 'qt'
    
    See also:
        http://ipython.org/ipython-doc/dev/interactive/qtconsole.html#qt-and-the-qtconsole
    
    """
    app, app_created = get_application()
    app.references = set()
    if not isinstance(window, QtGui.QWidget):
        window = window(**kwargs)
    app.references.add(window)
    window.show()
    if app_created:
        app.exec_()
    return window
    
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
            
