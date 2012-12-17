from python_qt_binding.QtCore import Qt 
from python_qt_binding import QtGui 
import os

__all__ = ['get_cursor']

getpath = lambda file: os.path.join(os.path.dirname(__file__), file)

def get_cursor(name):
    if name is None:
        name = 'ArrowCursor'
    if name == 'MagnifyingGlassCursor':
        MagnifyingGlassPixmap = QtGui.QPixmap(getpath("cursors/glass.png"))
        MagnifyingGlassPixmap.setMask(QtGui.QBitmap(\
                                      QtGui.QPixmap(getpath("cursors/glassmask.png"))))
        MagnifyingGlassCursor = QtGui.QCursor(MagnifyingGlassPixmap)
        return MagnifyingGlassCursor
    else:
        return QtGui.QCursor(getattr(Qt, name))
        
    