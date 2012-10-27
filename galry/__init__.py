"""Galry: high-performance interactive 2D visualization in Python"""

from debugtools import *

# import PyQT or Pyside
from python_qt_binding import QtCore, QtDeclarative, QtGui, \
    QtMultimedia, QtNetwork, QtOpenGL, QtXml

# HACK: we need to create a QT application before importing cursors,
# because one of the cursors makes use of QPixmap which requires 
# an active QApplication running
if QtCore.QCoreApplication.instance() is None:
    log_debug("creating QApplication in __init__ for creating cursors")
    import sys
    app = QtGui.QApplication(sys.argv)
    import cursors
    del app
    
from cursors import *
from tools import *
from galrywidget import *
from useractions import *
from interactionevents import *
from interactionmanager import *
from bindingmanager import *
from primitives import *
from templates import *
from dataloader import *
from paintmanager import *
from datanormalizer import *
