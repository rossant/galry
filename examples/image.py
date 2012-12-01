import os
from galry import *
import pylab as plt
import Image
import urllib, cStringIO

def load_image(url):
    """Download an image from an URL."""
    print "Downloading image... ",
    file = cStringIO.StringIO(urllib.urlopen(url).read())
    print "Done!"
    return Image.open(file)
   
class EarthPaintManager(PaintManager):
    def initialize(self):
        url = "http://earthobservatory.nasa.gov/blogs/elegantfigures/files/2011/10/globe_west_2048.jpg"
        texture = np.array(load_image(url))
        self.add_visual(TextureVisual, texture=texture,
            mipmap=True,  # use mipmapping, i.e. multiresolution texture 
            minfilter='LINEAR_MIPMAP_NEAREST',  # bilinear + mipmap filtering
            maxfilter='LINEAR'  # bilinear filtering
            )       

if __name__ == '__main__':
    # create window
    window = show_basic_window(paint_manager=EarthPaintManager,
                               constrain_ratio=True,
                               constrain_navigation=False,)
