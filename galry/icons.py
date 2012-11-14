import os
from python_qt_binding import QtCore
from python_qt_binding import QtGui

__all__ = ['get_icon']

def get_icon(name):
    path = os.path.dirname(os.path.realpath(__file__))
    path = os.path.join(path, "icons/%s.png" % name)
    return QtGui.QIcon(path)

