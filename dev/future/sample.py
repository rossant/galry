import sys
from OpenGL.GLUT import *
from OpenGL.GL import *
from OpenGL.GLU import *

def display():
    glClear(GL_COLOR_BUFFER_BIT)
    glFlush()

def init():
    glClearColor(0, 0, 0, 0)
    
def resize(w, h):
    pass

glutInit(sys.argv)
glutInitDisplayMode(GLUT_SINGLE | GLUT_RGBA)
glutInitWindowSize(600, 600)
glutInitWindowPosition(100, 100)
glutCreateWindow("Sample")
init()
glutDisplayFunc(display)
glutReshapeFunc(resize)
glutMainLoop()
