from galry import *
from numpy import *

# create 10 discs
plot(zeros(10), zeros(10), 'o', ms=50, is_static=True)

# position of 10 fingers
fingers = zeros((10, 2))

def anim(fig, param):
    # retrive the Leap motion frame
    frame = LEAP['frame']
    
    # update the finger positions
    fingers[:,:] = 10
    for i in xrange(len(frame.fingers)):
        pos = frame.fingers[i].tip_position
        x, y = pos.x / 255., pos.y / 255. - 1
        fingers[i,:] = (x, y)

    fig.set_data(position=fingers)

animate(anim, dt=.01)

show()

