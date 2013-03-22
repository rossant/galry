"""Debug script for finding out the OpenGL version.

Instructions:
  
  * run in a console:
  
        python gldebug.py
        
  * Send me the `galry_gldebug.txt` file created in the folder where
    you executed this script from.

"""
import os
import sys
import pprint

import numpy as np

from galry import *

# Capture stdout and stderr
class writer(object):
    log = []
    def write(self, data):
        self.log.append(data)
    def save(self, filename):
        with open(filename, 'w') as f:
            for line in self.log:
                f.write(line)

logger = writer()
sys.stdout = logger
sys.stderr = logger

class DebugVisual(PlotVisual):
    def initialize(self):
        super(DebugVisual, self).initialize(np.zeros(2))
        pprint.pprint(GLVersion.get_renderer_info())
        
figure(autodestruct=1)
visual(DebugVisual)
show()

filename = os.path.realpath('./galry_gldebug.txt')
logger.save(filename)

