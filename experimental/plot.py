# import galry.plot as plt
from galry import *
import numpy as np

# fig = figure()

X = np.random.randn(2, 1000)

# fig.imshow(np.random.rand(10, 10, 4), is_static=True)

plot(X, color=['r', 'y'])
text("Hello world!", coordinates=(.0, .9), is_static=True)


show()

