from galry import *
from numpy import *

n = 1000
x = linspace(-1., 1., n)
y = .5 * sin(10 * x)

X = np.vstack((y, y + 1))
plot(X, thickness=.02, color=['y','r'])

show()
