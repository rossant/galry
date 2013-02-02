from galry import *
from numpy import *

plot(zeros(10), zeros(10), 'o', ms=50, is_static=True)

mouse = zeros((10, 2))

def anim(fig, param):
    frame = LEAP['frame']
    
    mouse[:,:] = 10
    for i in xrange(len(frame.fingers)):
        pos = frame.fingers[i].tip_position
        x, y = pos.x / 255., pos.y / 255. - 1
        mouse[i,:] = (x, y)

    fig.set_data(position=mouse)

animate(anim, dt=.01)

show()

