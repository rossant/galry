"""Test plotting capabilities."""
from galry import *
from numpy import *
from numpy.random import randn

# multiple plots in a single call (most efficient)
Y = .05 * randn(10, 1000) + 1.5
plot(Y)

n = 10000
x = linspace(0, 1, n)

# scatter plot
y1 = .25 * random.randn(n)
plot(x, y1, 'oy')

# sine thick wave
y2 = sin(10 * x)
plot(x, y2, thickness=.01, color='r.5')

# static text
text("Hello World!", coordinates=(0, .9), is_static=True)

# specify the window boundaries
xlim(0, 1)
ylim(-2, 2)

# show the grid by default
grid()

show()


