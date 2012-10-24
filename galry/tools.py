import sys
import os
import numpy as np
import time
import timeit
import collections
import subprocess
from python_qt_binding import QtCore, QtGui, QtOpenGL
from functools import wraps
from debugtools import log_debug, log_info, log_warn

# try importing numexpr
try:
    import numexpr
except:
    numexpr = None
    
__all__ = [
'enum',
'extend_enum',
'show_window',
'run_all_scripts',
'enforce_dtype',
'repeat1D_fast',
'tile1D_fast',
'FpsCounter',
]
    
# Enumerations are just like global variables where each member
# is an int. Whenever a new enumeration is created, the numbers assigned to
# the enumeration members are increased by 100. Hence, there can be no more 
# than 100 members per enumeration.
ENUM_COUNT = 0
MAX_ENUM_SIZE = 100

def enum(*sequential, **named):
    """Create an enumeration."""
    global ENUM_COUNT, MAX_ENUM_SIZE
    i = ENUM_COUNT * MAX_ENUM_SIZE
    enums = dict(zip(sequential, range(i, i+len(sequential))), **named)
    enums["_dict"] = enums.copy()
    enums["__module__"] = __name__
    ENUM_COUNT += 1
    return type('Enum', (), enums)
    
def extend_enum(enum_base, enum_new):
    """Extend an enumeration with new values.
    
    The values are not changed.
    """
    d = dict(enum_base._dict, **enum_new._dict)
    return type('Enum', (), d)
    
def show_window(window, **kwargs):
    """Create a QT window in Python, or interactively in IPython with QT GUI
    event loop integration:
    
        # in ~/.ipython/ipython_config.py
        c.TerminalIPythonApp.gui = 'qt'
        c.TerminalIPythonApp.pylab = 'qt'
    
    See also:
        http://ipython.org/ipython-doc/dev/interactive/qtconsole.html#qt-and-the-qtconsole
    
    """
    app_created = False
    app = QtCore.QCoreApplication.instance()
    if app is None:
        log_debug("creating a new QApplication in order to show the window")
        app = QtGui.QApplication(sys.argv)
        app_created = True
    app.references = set()
    if not isinstance(window, QtGui.QWidget):
        window = window(**kwargs)
    app.references.add(window)
    window.show()
    if app_created:
        app.exec_()
    # import cursors
    # global cursors
    return window
    
def run_all_scripts(dir=".", autodestruct=True, condition=None):
    """Run all scripts successively."""
    if condition is None:
        condition = lambda file: file.endswith(".py") and not file.startswith("_")
    os.chdir(dir)
    for file in os.listdir(dir):
        if condition(file):
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
    return x.__array_interface__['data'][0]
    
def repeat1D_fast(arr, reps, step=1):
    c = np.lib.stride_tricks.as_strided(arr, (reps, arr.size), (0, step*arr.itemsize))
    c = c.T.ravel()
    return c
   
def tile1D_fast(arr, reps, step=1):
    c = np.lib.stride_tricks.as_strided(arr, (reps, arr.size), (0, step*arr.itemsize))
    c = c.ravel()
    return c
    
class FpsCounter(object):
    """Count FPS."""
    # memory for the FPS counter
    maxlen = 10
    
    def __init__(self, maxlen=None):
        if maxlen is None:
            maxlen = self.maxlen
        self.times = collections.deque(maxlen=maxlen)
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
            return 1. / max(.001, dif.min())
        else:
            return 0.
            
