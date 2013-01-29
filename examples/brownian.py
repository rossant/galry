"""Animated brownian motion."""
import numpy as np
from matplotlib.colors import hsv_to_rgb
from galry import *

class MyVisual(Visual):
    def initialize(self, X, color, T):
        n = X.shape[0]
        
        self.n = n
        self.size = n
        self.bounds = [0, n]
        self.primitive_type = 'LINE_STRIP'
        
        self.add_attribute('position', vartype='float', ndim=2, data=X)
        self.add_attribute('color', vartype='float', ndim=3, data=color)
        self.add_attribute('i', vartype='float', ndim=1, data=i)
        
        self.add_varying('vcolor', vartype='float', ndim=3)
        self.add_varying('vi', vartype='float', ndim=1)
        
        self.add_uniform('t', vartype='float', ndim=1, data=0.)
        
        self.add_vertex_main("""
        vcolor = color;
        vi = i;
        """)
        
        self.add_fragment_main("""
        out_color.rgb = vcolor;
        out_color.a = .1 * ceil(clamp(t - vi, 0, 1));
        """)

# number of steps
n = 1e6

# duration of the animation
T = 30.

b = np.array(np.random.rand(n, 2) < .5, dtype=np.float32)
b[b == True] = 1
b[b == False] = -1
X = np.cumsum(b, axis=0)

# print X
# exit()

# generate colors by varying linearly the hue, and convert from HSV to RGB
h = np.linspace(0., 1., n)
hsv = np.ones((1, n, 3))
hsv[0,:,0] = h
color = hsv_to_rgb(hsv)[0,...]
i = np.linspace(0., T, n)

m = X.min(axis=0)
M = X.max(axis=0)
center = (M + m)/2
X = 2 * (X - center) / (max(M) - min(m))

# current camera position
x = np.array([0., 0.])
y = np.array([0., 0.])

# filtering parameter
dt = .015

# zoom level
dx = .25

def anim(fig, params):
    global x, y, dx
    t, = params
    i = int(n * t / T) + 15000
    # follow the current position
    if i < n:
        y = X[i,:]
    # or unzoom at the end
    else:
        y *= (1 - dt)
        dx = np.clip(dx + dt * (1 - dx), 0, 1)
    if dx < .99:
        # filter the current position to avoid "camera shaking"
        x = x * (1 - dt) + dt * y    
        viewbox = [x[0] - dx, x[1] - dx, x[0] + dx, x[1] + dx]
        # set the viewbox
        fig.process_interaction('SetViewbox', viewbox)
        fig.set_data(t=t)

figure(constrain_ratio=True, toolbar=False)
visual(MyVisual, X, color, T)
animate(anim, dt=.01)
show()
