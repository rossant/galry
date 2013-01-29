"""Tutorial 2.2: Animation.

In this tutorial, we show how to animate objects to smoothly follow the
cursor.

"""

from galry import *
from numpy import *

# Number of discs.
n = 100

# Display n static discs with an opacity gradient.
color = ones((n, 4))
color[:,2] = 0
color[:,3] = linspace(0.01, 0.1, n)
plot(zeros(n), zeros(n), 'o', color=color, ms=50, is_static=True)

# Global variable with the current disc positions.
position = zeros((n, 2))

# Global variable with the current mouse position.
mouse = zeros((1, 2))

# Animation weights for each disc, smaller = slower movement.
w = linspace(0.03, 0.1, n).reshape((-1, 1))

# Update the mouse position.
def mousemove(fig, param):
    global mouse
    mouse[0,:] = param['mouse_position']

# Animate the object.
def anim(fig, param):
    # The disc position is obtained through a simple linear filter of the
    # mouse position.
    global position
    position += w * (-position + mouse)
    fig.set_data(position=position)
    
# We bind the "Move" action to the "mousemove" callback.
action('Move', mousemove)

# We bind the "Animate" event to the "anim" callback.
animate(anim, dt=.01)

show()
