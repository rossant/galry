import numpy as np
from default_template import DefaultTemplate
from datatemplate import DataTemplate
from ..primitives import PrimitiveType

__all__ = ['normalize',
           'projection_matrix', 'rotation_matrix', 'scale_matrix',
           'translation_matrix', 'camera_matrix',
           'ThreeDimensionsTemplate']

def normalize(x):
    if x.ndim == 1:
        return x / np.sqrt(np.sum(x ** 2))
    elif x.ndim == 2:
        return x / np.sqrt(np.sum(x ** 2, axis=1)).reshape((-1, 1))

def projection_matrix(angle, ratio, znear, zfar):
    return np.array([[1. / np.tan(angle), 0, 0, 0],
                     [0, ratio / np.tan(angle), 0, 0],
                     [0, 0, (zfar + znear) / (zfar - znear), 1],
                     [0, 0, -2. * zfar * znear / (zfar - znear), 0]])

def rotation_matrix(angle, axis=0):
    mat = np.eye(4)
    ind = np.array(sorted(list(set(range(3)).difference([axis]))))
    mat[np.ix_(ind,ind)] = np.array([[np.cos(angle), np.sin(angle)],
                               [-np.sin(angle), np.cos(angle)]])
    return mat
    
def scale_matrix(x, y, z):
    return np.diag([x, y, z, 1.])
    
def translation_matrix(x, y, z):
    return np.array([
      [1,      0,      0,       0],
      [0,      1,      0,       0], 
      [0,      0,      1,       0],
      [-x, -y, -z,  1]
    ])
    
def camera_matrix(eye, target, up):
    zaxis = normalize(target - eye)  # look at vector
    xaxis = normalize(np.cross(up, zaxis))  # right vector
    yaxis = normalize(np.cross(zaxis, xaxis))  # up vector
    
    orientation = np.array([
        [xaxis[0], yaxis[0], zaxis[0],     0],
        [xaxis[1], yaxis[1], zaxis[1],     0],
        [xaxis[2], yaxis[2], zaxis[2],     0],
        [      0,       0,       0,     1]
        ])
     
    translation = translation_matrix(*eye)
 
    return np.dot(translation, orientation)
    
    
    
    
    
    
    
    
    
class ThreeDimensionsTemplate(DataTemplate):

    def add_transformation(self, is_static=False):
        """Add static or dynamic position transformation."""
        
        # dynamic navigation
        if not is_static:
            self.add_uniform("transform", vartype="float", ndim=(4,4),
                size=None, data=np.eye(4))
            
            self.add_vertex_main("""
    //mat4 transform = get_transform(translation, scale, rotation);
    gl_Position = projection * camera * transform * gl_Position;""")
        # static
        else:
            self.add_vertex_main("""
    gl_Position = projection * camera * gl_Position;""")
        
    def add_constrain_ratio(self, constrain_ratio=False):
        """Add viewport-related code."""
        self.add_uniform("viewport", vartype="float", ndim=2)
        self.add_uniform("window_size", vartype="float", ndim=2)
        if constrain_ratio:
            self.add_vertex_main("gl_Position.xy = gl_Position.xy / viewport;")

            
    def initialize_default(self, is_static=False, constrain_ratio=False, **kwargs): 
        """Default initialization with navigation-related code."""
        self.is_static = is_static
        self.constrain_ratio = constrain_ratio
        
        self.add_transformation(is_static)
        self.add_constrain_ratio(constrain_ratio)
        
    
    def get_initialize_arguments(self, **data):
        pos = data.get("position", None)
        self.size = pos.shape[0]
        
    def initialize(self, camera_angle=None, camera_ratio=None,
        camera_zrange=None, **kwargs):
        
        # default camera parameters
        if camera_angle is None:
            camera_angle = np.pi / 4
        
        if camera_ratio is None:
            camera_ratio = 4./3.
            
        if camera_zrange is None:
            camera_zrange = (.5, 5.)
        
        # attributes
        self.add_attribute("position", vartype="float", ndim=3)
        self.add_attribute("normal", vartype="float", ndim=3)
        self.add_attribute("color", vartype="float", ndim=4)
        
        # varying color
        self.add_varying("varying_color", vartype="float", ndim=4)
        
        # default matrices
        projection = projection_matrix(camera_angle, camera_ratio, *camera_zrange)
        camera = camera_matrix(np.array([0., 0., -3.]),  # position
                               np.zeros(3),  # look at
                               np.array([0., 1., 0.]))  # top
        transform = np.eye(4)
                
        self.add_uniform("projection", ndim=(4, 4), size=None, data=projection)
        self.add_uniform("camera", ndim=(4, 4), size=None, data=camera)
        self.add_uniform("transform", ndim=(4, 4), size=None, data=transform)
        
        # diffuse and ambient light
        light_direction = normalize(np.array([0., 0., -1.]))
        ambient_light = .05
        self.add_uniform("light_direction", size=None, ndim=3, data=light_direction)
        self.add_uniform("ambient_light", size=None, ndim=1, data=ambient_light)
        
        # vertex shader with transformation matrices and basic lighting
        self.add_vertex_main("""
    gl_Position = vec4(position, 1.0);
    float light = dot(light_direction, normalize(mat3(camera) * mat3(transform) * normal));
    light = clamp(light, 0, 1);
    light = clamp(ambient_light + light, 0, 1);
    varying_color = color * light;
    varying_color.w = color.w;
        """)
        
        # basic fragment shader
        self.add_fragment_main("""
    out_color = varying_color;
        """)
        
        
        self.initialize_default(**kwargs)
        