import os
from galry import *
import pylab as plt

# time interval
DT = .01

# ball velocity
V = .5

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

class PongPaintManager(PaintManager):
    def get_score_text(self):
        """Return the score text."""
        return "%d - %d" % (self.score_left, self.score_right)
    
    def initialize(self):
        self.dt = DT
        
        # player positions
        self.pos = {}
        
        # scores
        self.score_left = 0
        self.score_right = 0
        
        # text visual
        self.add_visual(TextVisual, coordinates=(0., .9), text='',
            fontsize=32, name='score', color=(1.,) * 4)
            
        # initialize game
        self.new_game()
            
        # visuals
        self.add_visual(RectanglesVisual, coordinates=self.pos['left'],
            color=(1.,) * 4, name='left')
        self.add_visual(RectanglesVisual, coordinates=self.pos['right'],
            color=(1.,) * 4, name='right')
        self.add_visual(SpriteVisual, position=self.ball_pos, texture=get_tex(32),
            color=(1.,) * 4, name='ball')
            
    def get_player_pos(self, who):
        return (self.pos[who][0,1] + self.pos[who][0,3]) / 2.

    def move_player(self, who, dy):
        if np.abs(self.get_player_pos(who) + dy) > .95:
            return
        self.pos[who][0,[1,3]] += dy
        self.set_data(visual=who, coordinates=self.pos[who])
        
    def new_game(self):
        self.pos['left'] = np.array([[-.9, -DL, -.85, DL]])
        self.pos['right'] = np.array([[.9, -DL, .85, DL]])
        
        # ball position and velocity
        self.ball_pos = np.array([[0., 0.]])
        self.ball_v = np.array([[V, 0.]])  

        self.set_data(visual='left', coordinates=self.pos['left'])
        self.set_data(visual='right', coordinates=self.pos['right'])
        self.set_data(visual='score', text=self.get_score_text())
    
    def move_ball(self):
        x, y = self.ball_pos[0,:]
        v = self.ball_v
        
        # top/bottom collision
        if np.abs(y) >= .95:
            self.ball_v[0,1] *= -1
        
        # right collision
        py = None
        if x >= .82:
            py = self.get_player_pos('right')
            
        # left collision
        if x <= -.82:
            py = self.get_player_pos('left')
            
        if py is not None:
            # update ball velocity
            if np.abs(y - py) <= DL:
                self.ball_v[0,0] *= -1
                # rebound angle depending on the position of the rebound on 
                # the racket
                self.ball_v[0,1] = 3 * (y - py)
        
        # one player wins, next game
        if x >= .95:
            self.score_left += 1
            self.new_game()
        if x <= -.95:
            self.score_right += 1
            self.new_game()
        
        # ball position update
        self.ball_pos += self.ball_v * self.dt
            
    def update_callback(self):
        self.move_ball()
        self.set_data(visual='ball', position=self.ball_pos)
            
class PongInteractionManager(InteractionManager):
    def process_custom_event(self, event, parameter):
        if event == 'LeftPlayerMove':
            self.paint_manager.move_player('left', parameter)
        if event == 'RightPlayerMove':
            self.paint_manager.move_player('right', parameter)
        
class PongBindings(DefaultBindingSet):
    def initialize(self):
        self.set_fullscreen()
        self.extend()
    
    def extend(self):
        dx = .05

        # left player bindings
        self.set('KeyPressAction', 'LeftPlayerMove', key=QtCore.Qt.Key_W,
            param_getter=lambda p: dx)
        self.set('KeyPressAction', 'LeftPlayerMove', key=QtCore.Qt.Key_S,
            param_getter=lambda p: -dx)
        
        # right player bindings
        self.set('KeyPressAction', 'RightPlayerMove', key=QtCore.Qt.Key_Up,
            param_getter=lambda p: dx)
        self.set('KeyPressAction', 'RightPlayerMove', key=QtCore.Qt.Key_Down,
            param_getter=lambda p: -dx)
            
if __name__ == '__main__':
    print "Left player: Z/S keys\nRight player: Up/Down arrows\nF for fullscreen"
    
    # create window
    window = show_basic_window(paint_manager=PongPaintManager,
                               interaction_manager=PongInteractionManager,
                               bindings=PongBindings,
                               update_interval=DT)
