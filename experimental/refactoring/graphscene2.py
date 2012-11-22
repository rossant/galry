from numpy import *


v={'bounds': ([0, 3]),
              'constrain_navigation': False,
              'constrain_ratio': False,
              'fragment_shader': '\n//#version 120\n//precision mediump float;\n\nuniform vec2 viewport;\nuniform vec2 window_size;\n\nuniform vec4 color;\nuniform float point_size;\n\nvoid main()\n{\n    vec4 out_color = vec4(1.0, 1.0, 0.0, 1.0);\n    \n            out_color = color;\n                \n    gl_FragColor = out_color;\n}\n\n',
              'name': 'nodes',
              'primitive_type': 'LINE_STRIP',
              'size': 3,
              'variables': [
              
                            {'data': (1.0, 1.0),
                             'name': 'viewport',
                             'ndim': 2,
                             'shader_type': 'uniform',
                             'size': None,
                             'vartype': 'float'},
                             
                             
                            {'data': (600.0, 600.0),
                             'name': 'window_size',
                             'ndim': 2,
                             'shader_type': 'uniform',
                             'size': None,
                             'vartype': 'float'},
                             
                             
                            {'data': array([[-0.5, -0.5],
       [ 0.5, -0.5],
       [ 0.5,  0.5]], dtype=float32),
                             'name': 'position',
                             'ndim': 2,
                             'shader_type': 'attribute',
                             'size': None,
                             'vartype': 'float'},
                             
                             
                            {'data': (1.0, 1.0, 1.0, 1.0),
                             'name': 'color',
                             'ndim': 4,
                             'shader_type': 'uniform',
                             'size': None,
                             'vartype': 'float'},
                             
                             
                            {'data': 1.0,
                             'name': 'point_size',
                             'ndim': 1,
                             'shader_type': 'uniform',
                             'size': None,
                             'vartype': 'float'}
                             
                             ],
              'vertex_shader': '\n//#version 120\n//precision mediump float;\n\nuniform vec2 viewport;\nuniform vec2 window_size;\n\nuniform vec4 color;\nuniform float point_size;\nattribute vec2 position;\n\n        // Transform a position according to a given scaling and translation.\n        vec2 transform_position(vec2 position, vec2 scale, vec2 translation)\n        {\n        return scale * (position + translation);\n        }\n            \nvoid main()\n{\n    gl_PointSize = point_size;\n                gl_Position = vec4(position, \n                               0., 1.);\n}\n\n',
              }




              
              
              
              
              
v2 = {'bounds': ([0, 3]),
              'constrain_navigation': False,
              'constrain_ratio': False,
              'fragment_shader': '\n//#version 120\n//precision mediump float;\n\nuniform vec2 viewport;\nuniform vec2 window_size;\nuniform vec2 scale;\nuniform vec2 translation;\nuniform vec4 color;\nuniform float point_size;\n\nvoid main()\n{\n    vec4 out_color = vec4(1.0, 1.0, 0.0, 1.0);\n    \n            out_color = color;\n                \n    gl_FragColor = out_color;\n}\n\n',
              'name': 'nodes2',
              'primitive_type': 'LINE_STRIP',
              'size': 3,
              'variables': [
              
                    {'data': (1.0, 1.0),
                             'name': 'viewport',
                             'ndim': 2,
                             'shader_type': 'uniform',
                             'size': None,
                             'vartype': 'float'},
                             
                             
                            {'data': (600.0, 600.0),
                             'name': 'window_size',
                             'ndim': 2,
                             'shader_type': 'uniform',
                             'size': None,
                             'vartype': 'float'},
                             
                             
                            {'data': array([[ 0.5,  0.5],
       [-0.5,  0.5],
       [-0.5, -0.5]], dtype=float32),
                             'name': 'position',
                             'ndim': 2,
                             'shader_type': 'attribute',
                             'size': None,
                             'vartype': 'float'},
                             
                             
                            {'data': (1.0, 1.0, 1.0, 1.0),
                             'name': 'color',
                             'ndim': 4,
                             'shader_type': 'uniform',
                             'size': None,
                             'vartype': 'float'},
                             
                             
                            {'data': 1.0,
                             'name': 'point_size',
                             'ndim': 1,
                             'shader_type': 'uniform',
                             'size': None,
                             'vartype': 'float'}
                             
                             ],
              'vertex_shader': '\n//#version 120\n//precision mediump float;\n\nuniform vec2 viewport;\nuniform vec2 window_size;\n\nuniform vec4 color;\nuniform float point_size;\nattribute vec2 position;\n\n        // Transform a position according to a given scaling and translation.\n        vec2 transform_position(vec2 position, vec2 scale, vec2 translation)\n        {\n        return scale * (position + translation);\n        }\n            \nvoid main()\n{\n    gl_PointSize = point_size;\n                gl_Position = vec4(position, \n                               0., 1.);\n}\n\n',
              }
              
              
              
              
              
              
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
