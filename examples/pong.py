"""Pong video game example, can be played with two players on the
same computer.

Controls:
    Left player: D/C keys
    Right player: Up/Down arrows
    F for fullscreen

"""
import os
from galry import *
import pylab as plt

# time interval
DT = .01

# ball velocity
V = 1

# half-size of the racket
DL = .15

def get_tex(n):
    # ball texture
    tex = np.ones((n, n, 4))
    tex[:,:,0] = 1
    x = np.linspace(-1., 1., n)
    X, Y = np.meshgrid(x, x)
    R = X ** 2 + Y ** 2
    R = np.minimum(1, 3 * np.exp(-5*R))
    tex[:,:,-1] = R
    return tex
        
def get_player_pos(who):
    return (pos[who][0,1] + pos[who][0,3]) / 2.

def move_player(fig, who, dy):
    if np.abs(get_player_pos(who) + dy) > .95:
        return
    pos[who][0,[1,3]] += dy
    fig.set_data(visual=who, coordinates=pos[who])
    
def move_player_right(fig, dy):
    move_player(fig, 'right', dy)
def move_player_left(fig, dy):
    move_player(fig, 'left', dy)
    
def new_game(figure, parameter=None):
    pos['left'] = np.array([[-.9, -DL, -.85, DL]])
    pos['right'] = np.array([[.9, -DL, .85, DL]])
    
    # ball position and velocity
    
    global ball_pos, ball_v
    
    ball_pos = np.array([[0., 0.]])
    ball_v = np.array([[V, 0.]])  

    figure.set_data(visual='left', coordinates=pos['left'])
    figure.set_data(visual='right', coordinates=pos['right'])
    figure.set_data(visual='score', text="%d - %d" % (score_left, score_right))

def move_ball(figure):
    global ball_pos, ball_v
    global score_left, score_right
    
    x, y = ball_pos[0,:]
    v = ball_v
    
    # top/bottom collision
    if np.abs(y) >= .95:
        ball_v[0,1] *= -1
    
    # right collision
    py = None
    if x >= .82:
        py = get_player_pos('right')
        
    # left collision
    if x <= -.82:
        py = get_player_pos('left')
        
    if py is not None:
        # update ball velocity
        if np.abs(y - py) <= DL:
            ball_v[0,0] *= -1
            # rebound angle depending on the position of the rebound on 
            # the racket
            ball_v[0,1] = 3 * (y - py)
    
    # one player wins, next game
    if x >= .95:
        score_left += 1
        new_game(figure)
    if x <= -.95:
        score_right += 1
        new_game(figure)
    
    # ball position update
    ball_pos += ball_v * DT
        
def update(figure, parameter):
    t = parameter[0]
    move_ball(figure)
    figure.set_data(visual='ball', position=ball_pos)
    
fig = figure(toolbar=False)

ball_pos = np.array([[0., 0.]])
ball_v = np.array([[0, 0.]])  

# player positions
pos = {}

# scores
score_left = 0
score_right = 0

# text visual
visual(TextVisual, coordinates=(0., .9), text='',
    fontsize=32, name='score', color=(1.,) * 4)
    
# visuals
rectangles(coordinates=(0.,) * 4,
    color=(1.,) * 4, name='left')
rectangles(coordinates=(0.,) * 4,
    color=(1.,) * 4, name='right')
sprites(position=np.zeros((1, 2)), texture=get_tex(32),
    color=(1.,) * 4, name='ball')

dx = .05

# left player bindings
action('KeyPress', 'LeftPlayerMove', key='D',
    param_getter=lambda p: dx)
action('KeyPress', 'LeftPlayerMove', key='C',
    param_getter=lambda p: -dx)

# right player bindings
action('KeyPress', 'RightPlayerMove', key='Up',
    param_getter=lambda p: dx)
action('KeyPress', 'RightPlayerMove', key='Down',
    param_getter=lambda p: -dx)

event('RightPlayerMove', move_player_right)
event('LeftPlayerMove', move_player_left)

event('NewGame', new_game)
event('Initialize', new_game)

animate(update, dt=DT)

print "Left player: D/C keys\nRight player: Up/Down arrows\nF for fullscreen"
show()
