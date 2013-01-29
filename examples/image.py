"""Download an image and show it."""
# Necessary for future Python 3 compatibility
from __future__ import print_function
import os
from galry import *
from numpy import *
try:
    from PIL import Image
except Exception as e:
    raise ImportError("You need PIL for this example.")
import urllib, cStringIO

def load_image(url):
    """Download an image from an URL."""
    print("Downloading image... ", end="")
    file = cStringIO.StringIO(urllib.urlopen(url).read())
    print("Done!")
    return Image.open(file)
   
# new figure with ration constraining
figure(constrain_ratio=True, constrain_navigation=False,)

# download the image and convert it into a Numpy array
url = "http://earthobservatory.nasa.gov/blogs/elegantfigures/files/2011/10/globe_west_2048.jpg"
image = array(load_image(url))

# display the image
imshow(image, filter=True)

# show the image
show()


