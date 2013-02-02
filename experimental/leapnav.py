from galry import *
from numpy import *

def get_pos(vec):
    return array((vec.x, vec.y, vec.z))

def get_hand_pos(hand):
    pos = get_pos(hand.palm_position)
    if hand.fingers:
        pos = array([get_pos(finger.tip_position) for finger in hand.fingers])
    return pos
    
figure(constrain_navigation=True)
plot(random.randn(10000))
ylim(-5, 5)

h = None
dh = None
dhnew = 0.

h_fil = zeros(3)
dh_fil = 0.
dt = .1
h2n = None

def anim(fig, param):
    frame = LEAP['frame']
    
    if not frame:
        return
    
    global h, dh, dhnew, h_fil, dh_fil, h2n
        
    if frame.hands[0].fingers:
        
        pos = get_hand_pos(frame.hands[0]) / 100.
        hnew = pos.mean(axis=0)
        # dhnew = mean(abs(pos - hnew).sum(axis=1))
    
        if len(frame.hands) >= 2:
            pos2 = get_hand_pos(frame.hands[1]) / 100.
            h2new = pos2.mean(axis=0)
            dhnew = sum(abs(h2new - hnew))
            if h2n is None:
                h2n = dhnew
            dhnew = dhnew - h2n
            # print dhnew, h2n
        else:
            dh = None
            h2n = None
            # dhnew = dh
            
    
        if h is None:
            h = hnew
        if dh is None:
            dh = dhnew
        
        h_ = hnew - h
        h[:] = hnew
        dh_ = dhnew - dh
        dh = dhnew

        # filtering
        h_fil = h_fil + dt * (-h_fil + h_)
        dh_fil = dh_fil + dt * (-dh_fil + dh_)

        pan = (h_fil[0], 0)
        fig.process_interaction('Pan', pan)
        
        zoom = (dh_fil, 0, 0, 0)
        fig.process_interaction('Zoom', zoom)
        
        
    else:
        h = None
        dh = None
    

animate(anim, dt=.02)

show()

