# import galry.plot as plt
from galry import *
from galry.plot import PlotWidget

import numpy as np
import numpy.random as rdn

info_level()

widget = PlotWidget()

n = 1000
k = 3
X = np.linspace(-1., 1., n).reshape((1, -1))
X = np.tile(X, (k, 1))
Y = .1 * np.sin(20. * X)
Y += np.arange(k).reshape((-1, 1)) * .1

widget.paint_manager.add_plot(X, Y, color=['r1','y','b'])

win = create_basic_window(widget)
show_window(win)



# plt.figure()
# plt.subplot(121)  # LATER: subplot
# plt.text("Hello world",
        # x=0, # centered
        # y=1, # top
        # size=18, # font size
        # color='g',  # color
        # alpha=1.,  # transparency channel
        # bgcolor='w',  # background color
        # bgalpha=.5,  # background transparency
        # )
# # X and Y are NxM matrices
# plt.plot(X, Y,  # N plots
         # '-',  # style .-+xo
         # colors=colors,  # colors is a list of colors, one color for one line
         # size=5, # size of points or markers only
         # )

# plt.barplot(x, y, color='g')  # LATER
# plt.axes(0., 0.)  # LATER: display H/V data axes, going through that point
# plt.xlim(-1., 1.)  # LATER

# plt.show()  # data normalization happens here