from galry import *
import numpy as np

n = 300

# generate grid
x = np.linspace(-1., 1., n)
y = np.linspace(-1., 1., n)
X, Y = np.meshgrid(x, y)

# surface function
Z = .1*np.cos(10*X) * np.sin(10*Y)

surface(Z)

show()
