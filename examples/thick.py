from galry import *
from numpy import *

n = 1000
x = linspace(-1., 1., n)
y = .5 * sin(10 * x)
X = np.hstack((x.reshape((-1, 1)), y.reshape((-1, 1))))

w = .02
Y = np.zeros((2 * n, 2))
u = np.zeros((n, 2))
u[1:,0] = -np.diff(X[:,1])
u[1:,1] = np.diff(X[:,0])
r = (u[:,0] ** 2 + u[:,1] ** 2) ** .5
r[r == 0.] = 1
u[:,0] /= r
u[:,1] /= r
Y[::2,:] = X - w * u
Y[1::2,:] = X + w * u

plot(position=Y, primitive_type='TRIANGLE_STRIP')
ylim(-1, 1)
show()
