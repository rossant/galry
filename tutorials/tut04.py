"""Tutorial 04: Images.

In this tutorial, we show how to plot images.

"""

import os
from galry import *

# Specify that we want to constrain the ratio of the figure while navigating,
# since we'll show an image.
figure(constrain_ratio=True)

# We load the texture from an image using imread, which refers directly to
# the Matplotlib function.
path = os.path.dirname(os.path.realpath(__file__))
image = imread(os.path.join(path, 'images/earth.png'))

# We display the image and apply linear filtering and mipmapping.
# You can fine-tune the filtering with mipmap, minfilter, magfilter.
imshow(image, filter=True)

show()
