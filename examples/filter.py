import os
from galry import *
import pylab as plt

KERNELS = [
    'original',
    'sharpen',
    'sobel',
    'emboss',
    'blur',
    'derivex',
    'edges',
]
CURRENT_KERNEL_IDX = 0

def get_kernel(name='original'):
    kernel = np.zeros((3, 3))
    kernel[1, 1] = 1
    if name == "blur":
        kernel = np.array([[1,2,1],[2,4,2],[1,2,1]])
    if name == "sharpen":
        kernel = np.array([[0,-1,0],[-1,5,-1],[0,-1,0]])
    if name == "emboss":
        kernel = np.array([[-2,-1,0],[-1,1,1],[0,1,2]])
    if name == "derivex":
        kernel = np.array([[0,0,0],[-1,0,1],[0,0,0]])
    if name == "edges":
        kernel = np.array([[0,1,0],[1,-4,1],[0,1,0]])
    if name == "sobel":
        kernel = np.array([[1,0,-1],[2,0,-1],[1,0,-1]])
    
    kernel = np.array(kernel, dtype=np.float32)
    if kernel.sum() != 0:
        return kernel / float(kernel.sum())
    else:
        return kernel

def change_kernel(dir=1):
    global CURRENT_KERNEL_IDX
    CURRENT_KERNEL_IDX += dir
    CURRENT_KERNEL_IDX = np.mod(CURRENT_KERNEL_IDX, len(KERNELS))
    kernelname = KERNELS[CURRENT_KERNEL_IDX]
    return kernelname
        
class FilterVisual(TextureVisual):
    def initialize_fragment(self):
            
        # default identity kernel
        kernel = np.zeros((3, 3))
        kernel[1,1] = 1
        
        self.add_uniform("step", data=1. / self.texsize[0])
        self.add_uniform("kernel", vartype="float", ndim=(3,3), size=None,
            data=kernel)
                
        fragment = """
    // compute the convolution of the texture with the kernel
    out_color = vec4(0., 0., 0., 1.);
    for (int i = 0; i < 3; i++)
    {
        for (int j = 0; j < 3; j++)
        {
            out_color.xyz += kernel[i][j] * texture(tex_sampler, 
                varying_tex_coords + step * vec2(j - 1, i - 1)).xyz;
        }
    }
        """
            
        self.add_fragment_main(fragment)

class FilterPaintManager(PaintManager):
    def change_kernel(self, name):
        kernel = get_kernel(name)
        self.set_data(kernel=kernel, visual='image')
        self.set_data(text="%s filter" % name, visual='legend')
    
    def initialize(self):
        # get the absolute path of the file
        path = os.path.dirname(os.path.realpath(__file__))
        # load the texture from an image thanks to matplotlib
        texture = plt.imread(os.path.join(path, "images/lena.png"))
        # add a textured rectangle
        self.add_visual(FilterVisual, texture=texture, name='image')
        self.add_visual(TextVisual, text=" " * 32, name='legend',
            coordinates=(0,.95), is_static=True)
        
FilterEvents = enum("NextFilter",
                    "PreviousFilter")
        
class FilterInteractionManager(InteractionManager):
    def process_custom_event(self, event, parameter):
        # previous filter
        if event == FilterEvents.PreviousFilter:
            self.paint_manager.change_kernel(change_kernel(-1))
        # next filter
        if event == FilterEvents.NextFilter:
            self.paint_manager.change_kernel(change_kernel(1))
        
class FilterBinding(DefaultBindingSet):
    def extend(self):
        # left key
        self.set(UserActions.KeyPressAction,
                FilterEvents.PreviousFilter,
                key=QtCore.Qt.Key_Left)
        # right key
        self.set(UserActions.KeyPressAction,
                FilterEvents.NextFilter,
                key=QtCore.Qt.Key_Right)
        
if __name__ == '__main__':
    print "Press the left or right arrow on the keyboard to cycle through \
the filters."
    # create window
    window = show_basic_window(
        paint_manager=FilterPaintManager,
        interaction_manager=FilterInteractionManager,
        bindings=FilterBinding,
        constrain_ratio=True,
        constrain_navigation=True,
        size=(512,512))
