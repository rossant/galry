"""Tutorial 1.4: Images.

In this tutorial, we show how to plot images.

"""

import os
from galry import *
from numpy import *
from matplotlib.pyplot import imread

# Specify that we want to constrain the ratio of the figure while navigating,
# since we'll show an image.
figure(constrain_ratio=True)

# We load the texture from an image using imread, which refers directly to
# the Matplotlib function.
path = os.path.dirname(os.path.realpath(__file__))
image = imread(os.path.join(path, 'images/earth.png'))

# We display the image and apply linear filtering and mipmapping.
# Zoom in and try filter=False to see the difference.
# You can fine-tune the filtering with the mipmap, minfilter, magfilter
# arguments. When filter=True, the values are:
#   * mipmap=True,
#   * minfilter='LINEAR_MIPMAP_NEAREST',
#   * magfilter='LINEAR'.
imshow(image, filter=True)

show()
