import numpy as np
from visual import Visual
from galry import get_color

__all__ = ['normalize',
           'projection_matrix', 'rotation_matrix', 'scale_matrix',
           'translation_matrix', 'camera_matrix',
           'MeshVisual']

def normalize(x):
    """Normalize a vector or a set of vectors.
    
    Arguments:
      * x: a 1D array (vector) or a 2D array, where each row is a vector.
      
    Returns:
      * y: normalized copies of the original vector(s).
      
    """
    if x.ndim == 1:
        return x / np.sqrt(np.sum(x ** 2))
    elif x.ndim == 2:
        return x / np.sqrt(np.sum(x ** 2, axis=1)).reshape((-1, 1))

def projection_matrix(angle, ratio, znear, zfar):
    """Return a 4D projection matrix.
    
    Arguments:
      * angle: angle of the field of view, in radians.
      * ratio: W/H ratio of the field of view.
      * znear, zfar: near and far projection planes.
    
    Returns:
      * P: the 4x4 projection matrix.
      
    """
    return np.array([[1. / np.tan(angle), 0, 0, 0],
                     [0, ratio / np.tan(angle), 0, 0],
                     [0, 0, (zfar + znear) / (zfar - znear), 1],
                     [0, 0, -2. * zfar * znear / (zfar - znear), 0]])

def rotation_matrix(angle, axis=0):
    """Return a rotation matrix.
    
    Arguments:
      * angle: the angle of the rotation, in radians.
      * axis=0: the axis around which the rotation is made. It can be
        0 (rotation around x), 1 (rotation around y), 2 (rotation around z).
    
    Returns:
      * R: the 4x4 rotation matrix.
    
    """
    mat = np.eye(4)
    ind = np.array(sorted(list(set(range(3)).difference([axis]))))
    mat[np.ix_(ind,ind)] = np.array([[np.cos(angle), np.sin(angle)],
                               [-np.sin(angle), np.cos(angle)]])
    return mat
    
def scale_matrix(x, y, z):
    """Return a scaling matrix.
    
    Arguments:
      * x, y, z: the scaling coefficients in each direction.
      
    Returns:
      * S: the 4x4 projection matrix.
      
    """
    return np.diag([x, y, z, 1.])
    
def translation_matrix(x, y, z):
    """Return a translation matrix.
    
    Arguments:
      * x, y, z: the translation coefficients in each direction.
      
    Returns:
      * S: the 4x4 translation matrix.
      
    """
    return np.array([
      [1,      0,      0,       0],
      [0,      1,      0,       0], 
      [0,      0,      1,       0],
      [-x, -y, -z,  1]
    ])
    
def camera_matrix(eye, target=None, up=None):
    """Return a camera matrix.
    
    Arguments:
      * eye: the position of the camera as a 3-vector.
      * target: the position of the view target of the camera, as a 3-vector.
      * up: a normalized vector pointing in the up direction, as a 3-vector.
      
    Returns:
      * S: the 4x4 camera matrix.
      
    """
    if target is None:
        target = np.zeros(3)
    if up is None:
        target = np.array([0., 1., 0.])
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
    

class MeshVisual(Visual):
    """Template for basic 3D rendering.
    
    This template allows to render 3D vertices with 3D perspective and basic
    diffusive and ambient lighting.
    
    """
    def initialize_navigation(self, is_static=False):
        """Add static or dynamic position transformation."""
        
        # dynamic navigation
        if not is_static:
            self.add_uniform("transform", vartype="float", ndim=(4,4),
                size=None, data=np.eye(4))
            
            self.add_vertex_main("""
                gl_Position = projection * camera * transform * gl_Position;""",
                    position='last')
        # static
        else:
            self.add_vertex_main("""
                gl_Position = projection * camera * gl_Position;""")
        
    def initialize_default(self, is_static=False, constrain_ratio=False, **kwargs): 
        """Default initialization with navigation-related code."""
        self.is_static = is_static
        self.constrain_ratio = constrain_ratio
        self.initialize_navigation(is_static)
    
    def initialize(self, camera_angle=None, camera_ratio=None, autocolor=None,
        camera_zrange=None, position=None, color=None, normal=None, index=None,
        vertex_shader=None):
        """Initialize the template.
        
        Arguments:
          * camera_angle: the view angle of the camera, in radians.
          * camera_ratio: the W/H ratio of the camera.
          * camera_zrange: a pair with the far and near z values for the camera
            projection.
        
        Template fields are:
          * `position`: an attribute with the positions as 3D vertices,
          * `normal`: an attribute with the normals as 3D vectors,
          * `color`: an attribute with the color of each vertex, as 4D vertices.
          * `projection`: an uniform with the 4x4 projection matrix, returned by
            `projection_matrix()`.
          * `camera`: an uniform with the 4x4 camera matrix, returned by
            `camera_matrix()`.
          * `transform`: an uniform with the 4x4 transform matrix, returned by
            a dot product of `scale_matrix()`, `rotation_matrix()` and
            `translation_matrix()`.
          * `light_direction`: the direction of the diffuse light as a
            3-vector.
          * `ambient_light`: the amount of ambient light (white color).
            
        """
        
        if autocolor is not None:
            color = get_color(autocolor)
        
        
        # default camera parameters
        if camera_angle is None:
            camera_angle = np.pi / 4
        if camera_ratio is None:
            camera_ratio = 4./3.
        if camera_zrange is None:
            camera_zrange = (.5, 10.)
            
        self.size = position.shape[0]
        if self.primitive_type is None:
            self.primitive_type = 'TRIANGLES'
        
        # attributes
        self.add_attribute("position", vartype="float", ndim=3, data=position)
        self.add_attribute("normal", vartype="float", ndim=3, data=normal)
        self.add_attribute("color", vartype="float", ndim=4, data=color)
        if index is not None:
            self.add_index("index", data=index)
        
        # varying color
        self.add_varying("varying_color", vartype="float", ndim=4)
        
        # default matrices
        projection = projection_matrix(camera_angle, camera_ratio, *camera_zrange)
        camera = camera_matrix(np.array([0., 0., -4.]),  # position
                               np.zeros(3),              # look at
                               np.array([0., 1., 0.]))   # top
        transform = np.eye(4)
                
        # matrix uniforms
        self.add_uniform("projection", ndim=(4, 4), size=None, data=projection)
        self.add_uniform("camera", ndim=(4, 4), size=None, data=camera)
        self.add_uniform("transform", ndim=(4, 4), size=None, data=transform)
        
        # diffuse and ambient light
        light_direction = normalize(np.array([0., 0., -1.]))
        ambient_light = .25
        self.add_uniform("light_direction", size=None, ndim=3, data=light_direction)
        self.add_uniform("ambient_light", size=None, ndim=1, data=ambient_light)
        
        # vertex shader with transformation matrices and basic lighting
        if not vertex_shader:
            vertex_shader = """
            // convert the position from 3D to 4D.
            gl_Position = vec4(position, 1.0);
            // compute the amount of light
            float light = dot(light_direction, normalize(mat3(camera) * mat3(transform) * normal));
            light = clamp(light, 0, 1);
            // add the ambient term
            light = clamp(ambient_light + light, 0, 1);
            // compute the final color
            varying_color = color * light;
            // keep the transparency
            varying_color.w = color.w;
            """
        self.add_vertex_main(vertex_shader)
        
        # basic fragment shader
        self.add_fragment_main("""
            out_color = varying_color;
        """)
        
        # self.initialize_viewport(True)