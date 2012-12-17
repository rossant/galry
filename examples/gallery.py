"""Display all images in a directory."""

import Image
import numpy as np
import os
import sys
from galry import *

# load an image
def load(file, size=None):
    img = Image.open(file)
    if size is not None:
        img.thumbnail((size, size))
    return np.array(img)

# update the pointer to the next image
i = 0
def next(parameter=1):
    global i
    i = np.mod(i + parameter, len(files))

# return the current image and image ratio
def current():
    img = load(os.path.join(folder, files[i]), 5148/4)
    hi, wi, _ = img.shape
    ar = float(wi) / hi
    return img, ar

# callback function for the gallery navigation
def gotonext(figure, parameter):
    next(parameter)
    img, ar = current()
    figure.set_data(texture=img)
    figure.set_rendering_options(constrain_ratio=ar)
    figure.resizeGL(*figure.size)

# get list of images in the folder
if len(sys.argv) > 1:
    folder = sys.argv[1]
else:
    folder = '.'
files = sorted(filter(lambda f: f.lower().endswith('.jpg'), os.listdir(folder)))

if files:
    # get first image
    img, ar = current()

    # create a figure and show the filtered image    
    figure(constrain_ratio=ar, constrain_navigation=True)
    imshow(img, points=(-1., -1., 1., 1.), filter=True)

    # previous/next images with keyboard
    action('KeyPress', gotonext, key='Left', param_getter=-1)
    action('KeyPress', gotonext, key='Right', param_getter=1)

    show()
