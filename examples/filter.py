"""GPU-based image processing filters."""
import os
from galry import *
import pylab as plt

# we define a list of 3x3 image filter kernels
KERNELS = dict(
    original=np.array([[0,0,0],[0,1,0],[0,0,0]]),
    sharpen=np.array([[0,-1,0],[-1,5,-1],[0,-1,0]]),
    sobel=np.array([[1,0,-1],[2,0,-1],[1,0,-1]]),
    emboss=np.array([[-2,-1,0],[-1,1,1],[0,1,2]]),
    blur=np.array([[1,2,1],[2,4,2],[1,2,1]]),
    derivex=np.array([[0,0,0],[-1,0,1],[0,0,0]]),
    edges=np.array([[0,1,0],[1,-4,1],[0,1,0]]),
)

# current kernel index
CURRENT_KERNEL_IDX = 0

# we specialize the texture visual (which displays a 2D image) to add
# GPU filtering capabilities
class FilterVisual(TextureVisual):
    def initialize_fragment(self):
        # elementary step in the texture, where the coordinates are normalized
        # in [0, 1]. The step is then 1/size of the texture.
        self.add_uniform("step", data=1. / self.texsize[0])
        
        # uniform 3x3 matrix variable
        self.add_uniform("kernel", vartype="float", ndim=(3,3),
            data=KERNELS['original'])
            
        # we add some code in the fragment shader which computes the filtered
        # texture
        self.add_fragment_main("""
        /* Compute the convolution of the texture with the kernel */
        
        // The output color is a vec4 variable called `out_color`.
        out_color = vec4(0., 0., 0., 1.);
        
        // We compute the convolution.
        for (int i = 0; i < 3; i++)
        {
            for (int j = 0; j < 3; j++)
            {
                // The variables are those defined in the base class
                // TextureVisual.
                out_color.xyz += kernel[i][j] * texture2D(tex_sampler, 
                    varying_tex_coords + step * vec2(j - 1, i - 1)).xyz;
            }
        }
        """)

def change_kernel(figure, parameter):
    # we update the kernel index
    global CURRENT_KERNEL_IDX
    CURRENT_KERNEL_IDX += parameter
    CURRENT_KERNEL_IDX = np.mod(CURRENT_KERNEL_IDX, len(KERNELS))
    # we get the kernel name and matrix
    name = KERNELS.keys()[CURRENT_KERNEL_IDX]
    kernel = np.array(KERNELS[name], dtype=np.float32)
    # we normalize the kernel
    if kernel.sum() != 0:
        kernel = kernel / float(kernel.sum())
    # now we change the kernel variable in the image
    figure.set_data(kernel=kernel, visual='image')
    # and the text in the legend
    figure.set_data(text="%s filter" % name, visual='legend')

# create square figure
figure(constrain_ratio=True, constrain_navigation=True, figsize=(512,512))

# load the texture from an image thanks to matplotlib
path = os.path.dirname(os.path.realpath(__file__))
texture = plt.imread(os.path.join(path, "images/lena.png"))

# we add our custom visual
visual(FilterVisual, texture=texture, name='image')

# we add some text
text(text='original filter', name='legend', coordinates=(0,.95), is_static=True)

# add left and right arrow action handler
action('KeyPress', change_kernel, key='Left', param_getter=-1)
action('KeyPress', change_kernel, key='Right', param_getter=1)

show()
