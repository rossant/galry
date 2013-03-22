"""Debug script for finding out the OpenGL version.

Instructions:
  
  * run in a console:
  
        python gldebug.py
        
  * Send me the `galry_gldebug.txt` file created in the folder where
    you executed this script from.

"""
import os
import pprint
import numpy as np
from galry import *

class DebugVisual(PlotVisual):
    def initialize(self):
        super(DebugVisual, self).initialize(np.zeros(2))
        filename = os.path.realpath('./galry_gldebug.txt')
        with open(filename, 'w') as f:
            pprint.pprint(GLVersion.get_renderer_info(), f)
        
figure(autodestruct=1)
visual(DebugVisual)
show()
