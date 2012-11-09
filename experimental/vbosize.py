from PyQt4 import QtGui, QtCore, QtOpenGL
from PyQt4.QtOpenGL import QGLWidget
import OpenGL.GL as gl
# import OpenGL.arrays.vbo as glvbo

class GLPlotWidget(QGLWidget):
    width, height = 600, 600
    
    def set_data(self, data):
        self.data = data
        self.count = data.shape[0]
    
    def initializeGL(self):
        gl.glClearColor(0,0,0,0)
        self.vbo = gl.glGenBuffers(1)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.vbo)
        gl.glBufferData(gl.GL_ARRAY_BUFFER, self.data, gl.GL_DYNAMIC_DRAW)
        
    def paintGL(self):
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)
        gl.glColor(1,1,0)            
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.vbo)
        gl.glEnableClientState(gl.GL_VERTEX_ARRAY)
        gl.glVertexPointer(2, gl.GL_FLOAT, 0, None)
        gl.glDrawArrays(gl.GL_LINE_STRIP, 0, self.count)
        
    def resizeGL(self, width, height):
        self.width, self.height = width, height
        gl.glViewport(0, 0, width, height)
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        gl.glOrtho(-1, 1, -1, 1, -1, 1)
        
if __name__ == '__main__':
    import sys
    import numpy as np
    import numpy.random as rdn
    
    N = 1e6

    class TestWindow(QtGui.QMainWindow):
        def __init__(self):
            super(TestWindow, self).__init__()
            data = .01 * np.array(rdn.randn(N, 2), dtype=np.float32)
            data[:,1] += .5
            data[N-1000:,:] -= .5
            self.widget = GLPlotWidget()
            self.widget.set_data(data)
            self.setGeometry(100, 100, self.widget.width, self.widget.height)
            self.setCentralWidget(self.widget)
            self.show()
    
    app = QtGui.QApplication(sys.argv)
    window = TestWindow()
    window.show()
    app.exec_()
    