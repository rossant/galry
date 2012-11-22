VS = """
#version 100
//precision mediump float;

attribute vec2 position;
uniform vec2 viewport;

vec2 transform_position(vec2 position, vec2 scale, vec2 translation)
{
return scale * (position + translation);
}
            
void main()
{
    vec2 scale = vec2(1., 1.);
    vec2 translation = vec2(0., 0.);
    gl_Position = vec4(transform_position(position, scale, translation), 
                   0., 1.);
                   
    gl_Position.xy = gl_Position.xy / viewport;
    
    gl_PointSize = 16;
}
"""

FS = """
#version 100
//precision mediump float;

uniform sampler2D tex;

uniform vec4 color;

void main()
{
    vec4 out_color = vec4(1., 1., 1., 1.);
    //out_color = color;
    
    out_color = texture2D(tex, gl_PointCoord) * color;
        
    gl_FragColor = out_color;
}
"""

import numpy as np
import numpy.random as rdn
position = np.array(.2 * rdn.randn(100, 2), dtype=np.float32)
tex = np.array(np.random.rand(16, 16, 4) * .5, dtype=np.float32)
index = np.array(np.arange(len(position)) / 10, dtype=np.int32)

# A Scene is made of multiple visuals, homogeneous sets of primitives rendered
# in a single call with OpenGL.
GraphScene = {
    'visuals': 
    [   
        {
            'name': 'nodes',
            'size': len(position),
            'primitive_type': 'POINTS',
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
                'name': 'index',
                'shader_type': 'index',
                'data': index,
                },
                
                {
                'name': 'color',
                'vartype': 'float',
                'ndim': 4,
                'shader_type': 'uniform',
                'data': (1., 1., 0., 1.),
                },
                
                {
                'name': 'tex',
                'ndim': 2,
                'ncomponents': 4,
                'size': (16, 16),
                'shader_type': 'texture',
                'data': tex,
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

