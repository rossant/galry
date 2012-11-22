from numpy import *

VS = """
attribute vec2 position;
uniform vec2 viewport;

void main()
{
    gl_Position = vec4(position, 0, 1);
}
"""

FS = """

uniform vec4 color;

void main()
{
    vec4 out_color = vec4(1., 1., 1., 1.);
    //out_color = color;    
    gl_FragColor = out_color;
}
"""

import numpy as np
import numpy.random as rdn
position = array([[-0.5, -0.5],
       [ 0.5, -0.5],
       [ 0.5,  0.5]], dtype=float32)

position2 = array([[ 0.5,  0.5],
       [-0.5,  0.5],
       [-0.5, -0.5]], dtype=float32)
       
       

v =         {
            'name': 'nodes',
            'size': len(position),
            'bounds': [0, len(position)],
            'primitive_type': 'LINE_STRIP',
            'constrain_ratio': False,
            'constrain_navigation': False,
            'variables': 
            [
                {
                'name': 'position',
                'id': 'node_position',
                'vartype': 'float',
                'ndim': 2,
                'shader_type': 'attribute',
                'data': position,
                },
                
                {
                'name': 'color',
                'vartype': 'float',
                'ndim': 4,
                'shader_type': 'uniform',
                'data': (1., 1., 0., 1.),
                },
                
                {
                'name': 'viewport',
                'vartype': 'float',
                'ndim': 2,
                'shader_type': 'uniform',
                'data': (1., 1.),
                },
                
                {
                'name': 'window_size',
                'vartype': 'float',
                'ndim': 2,
                'shader_type': 'uniform',
                'data': (600., 600.),
                },
            ],
            'vertex_shader': VS,
            'fragment_shader': FS,
        }


        
        
        
        
v2 =         {
            'name': 'nodes2',
            'size': len(position),
            'bounds': [0, len(position)],
            'primitive_type': 'LINE_STRIP',
            'constrain_ratio': False,
            'constrain_navigation': False,
            'variables': 
            [
                {
                'name': 'position',
                'id': 'node_position',
                'vartype': 'float',
                'ndim': 2,
                'shader_type': 'attribute',
                'data': position2,
                },
                
                {
                'name': 'color',
                'vartype': 'float',
                'ndim': 4,
                'shader_type': 'uniform',
                'data': (1., 1., 0., 1.),
                },
                
                {
                'name': 'viewport',
                'vartype': 'float',
                'ndim': 2,
                'shader_type': 'uniform',
                'data': (1., 1.),
                },
                
                {
                'name': 'window_size',
                'vartype': 'float',
                'ndim': 2,
                'shader_type': 'uniform',
                'data': (600., 600.),
                },
            ],
            'vertex_shader': VS,
            'fragment_shader': FS,
        }


        
        
        
        
        
# A Scene is made of multiple visuals, homogeneous sets of primitives rendered
# in a single call with OpenGL.
GraphScene = {
    'visuals': 
    [   v, v2
    ],
    'renderer_options':
    {
        'activate3D': False,
        'antialiasing': False,
        'transparency': True,
        'sprites': True,
        'background': (0, 0, 0, 0),
    }
}

