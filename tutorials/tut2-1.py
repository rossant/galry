"""Tutorial 2.1: Text and interaction.

In this tutorial, we show how to display text and we give a first example
of the interaction system.

"""

from galry import *
from numpy import *

# This function takes x, y coordinates of the mouse and return a text.
def get_text(*pos):
    return "The mouse is at ({0:.2f}, {1:.2f}).".format(*pos)

# This is a callback function for the MouseMoveAction. The first parameter
# is the figure, the second a dictionary with parameters about the user
# actions (mouse, keyboard, etc.).
def mousemove(fig, params):
    # We get the text to display.
    text = get_text(*params['mouse_position'])
    
    # We update the text dynamically.
    fig.set_data(text=text, visual='mytext')

# We display a text and give it a unique name 'mytext' so that we can 
# refer to this visual in the mouse move callback. We also specify that
# this text should be fixed and not transformed while panning and zooming.
text("Move your mouse!", name='mytext', fontsize=22, is_static=True)

# We bind the mouse move action to the mousemove callback.
action('Move', mousemove)

show()
