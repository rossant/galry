from galry import NavigationEventProcessor, InteractionManager, \
    PaintManager, \
    GridEventProcessor, scale_matrix, rotation_matrix, translation_matrix, \
    MeshNavigationEventProcessor
from default_manager import DefaultPaintManager, DefaultInteractionManager, \
    DefaultBindings
from plot_manager import PlotBindings
import numpy as np


def load_mesh(filename):
    """Load vertices and faces from a wavefront .obj file and generate
    normals.
    
    """
    data = np.genfromtxt(filename, dtype=[('type', np.character, 1),
                                          ('points', np.float32, 3)])

    # Get vertices and faces
    vertices = data['points'][data['type'] == 'v']
    faces = (data['points'][data['type'] == 'f']-1).astype(np.uint32)

    # Build normals
    T = vertices[faces]
    N = np.cross(T[::,1 ]-T[::,0], T[::,2]-T[::,0])
    L = np.sqrt(N[:,0]**2+N[:,1]**2+N[:,2]**2)
    N /= L[:, np.newaxis]
    normals = np.zeros(vertices.shape)
    normals[faces[:,0]] += N
    normals[faces[:,1]] += N
    normals[faces[:,2]] += N
    L = np.sqrt(normals[:,0]**2+normals[:,1]**2+normals[:,2]**2)
    normals /= L[:, np.newaxis]

    # Scale vertices such that object is contained in [-1:+1,-1:+1,-1:+1]
    vmin, vmax =  vertices.min(), vertices.max()
    vertices = 2*(vertices-vmin)/(vmax-vmin) - 1

    return vertices, normals, faces

         
class MeshInteractionManager(DefaultInteractionManager):
    def initialize_default(self, constrain_navigation=None, momentum=None):
        super(MeshInteractionManager, self).initialize_default()
        self.add_processor(MeshNavigationEventProcessor, name='navigation')
        self.add_processor(GridEventProcessor, name='grid')
        
        
class MeshPaintManager(DefaultPaintManager):
    def initialize_default(self, *args, **kwargs):
        super(MeshPaintManager, self).initialize_default(*args, **kwargs)
        self.set_rendering_options(activate3D=True)
        
        
class MeshBindings(PlotBindings):
    def initialize(self):
        super(MeshBindings, self).initialize()
        self.set_rotation_mouse()
        self.set_rotation_keyboard()
    
    def set_panning_mouse(self):
        # Panning: CTRL + left button mouse
        self.set('LeftClickMove', 'Pan',
                    # key_modifier='Control',
                    param_getter=lambda p: (-4*p["mouse_position_diff"][0],
                                            -4*p["mouse_position_diff"][1]))
        
    def set_rotation_mouse(self):
        # Rotation: left button mouse
        self.set('MiddleClickMove', 'Rotation',
                    param_getter=lambda p: (3*p["mouse_position_diff"][0],
                                            3*p["mouse_position_diff"][1]))    

        self.set('LeftClickMove', 'Rotation',
                    key_modifier='Control',
                    param_getter=lambda p: (3*p["mouse_position_diff"][0],
                                            3*p["mouse_position_diff"][1]))    
             
    def set_rotation_keyboard(self):
        """Set zooming bindings with the keyboard."""
        # Rotation: ALT + key arrows
        self.set('KeyPress', 'Rotation',
                    key='Left', key_modifier='Shift', 
                    param_getter=lambda p: (-.25, 0))
        self.set('KeyPress', 'Rotation',
                    key='Right', key_modifier='Shift', 
                    param_getter=lambda p: (.25, 0))
        self.set('KeyPress', 'Rotation',
                    key='Up', key_modifier='Shift', 
                    param_getter=lambda p: (0, .25))
        self.set('KeyPress', 'Rotation',
                    key='Down', key_modifier='Shift', 
                    param_getter=lambda p: (0, -.25))
                    
    def set_zoombox_mouse(self):
        """Deactivate zoombox."""
        pass

    def set_zoombox_keyboard(self):
        """Deactivate zoombox."""
        pass
    
    def extend(self):
        """Set rotation interactions with mouse and keyboard."""
        self.set_rotation_mouse()
        self.set_rotation_keyboard()
        
        