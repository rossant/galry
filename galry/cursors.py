from python_qt_binding.QtCore import Qt 
from python_qt_binding import QtGui 
import os

__all__ = [
    'ArrowCursor',
    'OpenHandCursor',
    'ClosedHandCursor',
    'CrossCursor',
    'MagnifyingGlassCursor',
]

ArrowCursor = None
OpenHandCursor = None
ClosedHandCursor = None
CrossCursor = None
MagnifyingGlassCursor = None

getpath = lambda file: os.path.join(os.path.dirname(__file__), file)

def load():
    """Load all cursors.
    
    Important note: this function must be called after QT initialization,
    more precisely a QApplication must be running.
    
    """
    global ArrowCursor, OpenHandCursor, ClosedHandCursor, CrossCursor, \
            MagnifyingGlassCursor

    ArrowCursor = QtGui.QCursor(Qt.ArrowCursor)
    OpenHandCursor = QtGui.QCursor(Qt.OpenHandCursor)
    ClosedHandCursor = QtGui.QCursor(Qt.ClosedHandCursor)
    CrossCursor = QtGui.QCursor(Qt.CrossCursor)
    
    MagnifyingGlassPixmap = QtGui.QPixmap(getpath("cursors/glass.png"))
    MagnifyingGlassPixmap.setMask(QtGui.QBitmap(\
                                  QtGui.QPixmap(getpath("cursors/glassmask.png"))))
    MagnifyingGlassCursor = QtGui.QCursor(MagnifyingGlassPixmap)
    
    
    
    
