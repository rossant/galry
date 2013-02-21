from galry import *
from numpy import *

n = 10000
x = linspace(-1., 1., n)

plot(x, np.sin(10*x), thickness=.02)

show()
