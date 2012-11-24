from zmq.utils import jsonapi
import numpy as np
import base64
from galry import *
from galry.galryplot import GalryPlot
from galry.primitives import PrimitiveType, GL_PRIMITIVE_TYPE_CONVERTER

"""
%load_ext ipynbgalry
from IPython.display import display
from galry.galryplot import GalryPlot
a = GalryPlot()
display(a)
"""

    
     
# Python handler
def get_json(plot=None):
    """This function takes the displayed object and returns a JSON string
    which will be loaded by the Javascript handler."""

    return plot.serialize()
    
_loaded = False

def load_ipython_extension(ip):
    """Load the extension in IPython."""
    global _loaded
    if not _loaded:
        # Get the formatter.
        mime = 'application/json'
        formatter = ip.display_formatter.formatters[mime]

        # Register handlers.
        # The first argument is the full module name where the class is defined.
        # The second argument is the class name.
        # The third argument is the Python handler that takes an instance of
        # this class, and returns a JSON string.
        formatter.for_type_by_name('galry.galryplot', 'GalryPlot', get_json)

        _loaded = True

    