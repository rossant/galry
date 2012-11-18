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

def encode_data(data):
    return base64.b64encode(data)

def get_template_json(template, dataholder):
    """Serialize a template and its corresponding data holder."""
    vs, fs = template.get_shader_codes()
    
    result = {}
    ptype = str(GL_PRIMITIVE_TYPE_CONVERTER[template.primitive_type])[3:]
    ptype = ptype[:ptype.index(' ')]
    
    result['template'] = {
        'primitive_type': ptype,
        
        'vertex_shader': vs,
        'fragment_shader': fs,
    }
    
    result['template']['attributes'] = {}
    for name, attr in template.attributes.iteritems():
        result['template']['attributes'][name] = dict(ndim=attr['ndim'])
    
    result['template']['uniforms'] = {}
    for name, uniform in template.uniforms.iteritems():
        result['template']['uniforms'][name] = dict(
            ndim=uniform['ndim'],
            size=uniform.get('size', False),
            vartype=uniform['vartype'])
            
    result['template']['varyings'] = {}
    for name, uniform in template.varyings.iteritems():
        result['template']['varyings'][name] = dict(
            ndim=uniform['ndim'],
            vartype=uniform['vartype'])

    result['dataholder'] = {
        'size': template.size,
    }
    
    # set specified data first
    for name, data in dataholder.iteritems():
        if isinstance(data, np.ndarray):
            data = encode_data(data)
        result['dataholder'][name] = data
    # then, complete with default data if necessary
    for name, attr in template.attributes.iteritems():
        data = attr.get('data', None)
        if name not in result['dataholder'] and data is not None:
            result['dataholder'][name] = data
    for name, attr in template.uniforms.iteritems():
        data = attr.get('data', None)
        if name not in result['dataholder'] and data is not None:
            result['dataholder'][name] = data
    
    
    return result
    
     
# Python handler
def get_json(plot=None):
    """This function takes the displayed object and returns a JSON string
    which will be loaded by the Javascript handler."""
    
    # We first create a Python dict with the JSON fields and values.
    result = {}
    
    # Specify the javascript handler.
    result['handler'] = 'GalryPlotHandler'  # name of the handler

    w = plot.get_widget()()
    w.initializeGL()

    # log_info(str(w.paint_manager.datasets))
    template = w.paint_manager.datasets[0]["template"]
    loader = w.paint_manager.datasets[0]["loader"]
    
    # log_info(str(template))
    # log_info(str(loader))
    
    dh = {}
    for name, data in loader.attributes.iteritems():
        dh[name] = data['data']
    for name, data in loader.uniforms.iteritems():
        dh[name] = data['data']
    
    result.update(get_template_json(template, dh))
    
    js = jsonapi.dumps(result)
    
    # log_info(js)
    
    return js

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

        
# if __name__ == '__main__':
    # w = cr()
    # print get_json(w)
    
    
    