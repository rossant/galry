High level interface
--------------------

### Ideas

from galry.plot import *

# otherwise, a figure is internally created in the namespace
fig = figure()

# plotting
fig.plot(x, y, '--r', name='myplot')
fig.text(text, position)

# events
def lmm(fig, parameters):
    # fig is an object used to update data in visuals and that contains
    # all information related to the figure. parameters is a dict with
    # all information related to the user actions
    for v in fig.visuals():
        fig.set_data(v, ...)
        
    fig.set_data('myplot', ...)
    
fig.left_mouse_move(lmm)
fig.left_click("MyClickEvent")
fig.event("MyClickEvent", callback)

# create and show window
fig.show()


These commands allow to create internally a custom paint manager and 
interaction manager, which will then be used in show when creating the
window.
For the plotting commands, fig.xxx(...) <==> pm.add_visual(Xxx, ...)





Notes about the future high-level interface. It should be as close as possible
from the matplotlib interface.

### Example:
        
    import galry.plot as plt

    plt.figure()
    plt.subplot(121)  # LATER: subplot
    plt.text("Hello world",
            x=0, # centered
            y=1, # top
            size=18, # font size
            color='g',  # color
            alpha=1.,  # transparency channel
            bgcolor='w',  # background color
            bgalpha=.5,  # background transparency
            )
    # X and Y are NxM matrices
    plt.plot(X, Y,  # N plots
             '-',  # style .-+xo
             colors=colors,  # colors is a list of colors, one color for one line
             size=5, # size of points or markers only
             )

    plt.barplot(x, y, color='g')  # LATER
    plt.axes(0., 0.)  # LATER: display H/V data axes, going through that point
    plt.xlim(-1., 1.)  # LATER

    plt.show()  # data normalization happens here

LATER: Basic GUI? with Home (reset view), Save
    
    
### Interactions
  * navigation with mouse and keyboard
  * CTRL + keyboard/wheel/mouse: zoom x or y
  * SHIFT + wheel/mouse: pan x or y
  * press I: info, with H/V lines following the mouse and cursor coordinates
    then, CTRL + mouse move makes the line rotate, and display the slope 
    (H/V lines still visible)
    
  * CTRL + S: save image

### Colors

Several possibilities to specify a color:

  * 'r'  # among rgbcymkw
  * 'r0.5'  # color and transparency
  * '#ff0000'  # hexadecimal code
  * '#ff0000a0'  # hexadecimal code + transparency
  * (1., 0., 0.)  # RGB
  * (1., 0., 0., .5)  # RGBA

### LATER: Signal plot

  * Longsignal plot: for viewing long analog continuous signals that 
    cannot fit on screen or in system memory (hdf5). An horizontal scrollbar
    allows to scroll along time, new data is loaded transparently

    plt.signal(X,  # a N x M matrix, N signals, M samples per signal
               freq=20000.,  # sampling frequency
               cache=10.,  # cache duration, in seconds



