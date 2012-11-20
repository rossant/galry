from PyQt4 import QtGui, QtCore, QtOpenGL
from PyQt4.QtOpenGL import QGLWidget
import OpenGL.GL as gl
# import OpenGL.arrays.vbo as glvbo

    
count = 10
samples = 5000000
N = count * samples


class GLPlotWidget(QGLWidget):
    width, height = 600, 600
    
    def set_data(self, data):
        self.data = data
        self.size = data.shape[0]
        self.color = np.array(np.ones((self.size, 4)), dtype=np.float32)
    
    def initializeGL(self):
        gl.glClearColor(0,0,0,0)
        self.vbo = gl.glGenBuffers(1)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.vbo)
        gl.glBufferData(gl.GL_ARRAY_BUFFER, self.data, gl.GL_DYNAMIC_DRAW)
        
        self.cbo = gl.glGenBuffers(1)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.cbo)
        gl.glBufferData(gl.GL_ARRAY_BUFFER, self.color, gl.GL_DYNAMIC_DRAW)
        
        self.count = count
        self.first = np.array(np.arange(0, self.size, samples), dtype=np.int32)
        self.counts = samples * np.ones(count, dtype=np.int32)
        
    def paintGL(self):
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)

        gl.glEnableClientState(gl.GL_VERTEX_ARRAY)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.vbo)
        gl.glVertexPointer(2, gl.GL_FLOAT, 0, None)
        
        gl.glEnableClientState(gl.GL_COLOR_ARRAY)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.cbo)
        gl.glColorPointer(4, gl.GL_FLOAT, 0, None)
        
        gl.glMultiDrawArrays(gl.GL_LINE_STRIP, self.first, self.counts, self.count)
        
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

    class TestWindow(QtGui.QMainWindow):
        def __init__(self):
            super(TestWindow, self).__init__()
            data = .05 * np.array(rdn.randn(1, 2), dtype=np.float32)
            data = np.tile(data, (N, 1))
            data[-1,:] += .5
            self.widget = GLPlotWidget()
            self.widget.set_data(data)
            self.setGeometry(100, 100, self.widget.width, self.widget.height)
            self.setCentralWidget(self.widget)
            self.show()
    
    app = QtGui.QApplication(sys.argv)
    window = TestWindow()
    window.show()
    app.exec_()
    