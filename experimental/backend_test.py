

import matplotlib
matplotlib.use('module://backend_galry')


import matplotlib.pyplot as plt
import numpy as np

x = np.linspace(-1., 1., 1000)
y = np.sin(20 * x)

plt.plot(x, y)
plt.show()

