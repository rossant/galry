from galry import *
from numpy import *

n = 1000
x = linspace(-1., 1., n)
y = .5 * sin(10 * x)
X = np.hstack((x.reshape((-1, 1)), y.reshape((-1, 1))))

plot(position=X, thickness=.05)
ylim(-1, 1)
show()
