"""GPU-based interactive Mandelbrot fractal example."""
from galry import *
import numpy as np
import numpy.random as rdn

FSH = """
// take a position and a number of iterations, and
// returns the first iteration where the system escapes a box of size N.
int mandelbrot_escape(vec2 pos, int iterations)
{
vec2 z = vec2(0., 0.);
int n = 0;
int N = 10;
int N2 = N * N;
float r2 = 0.;
for (int i = 0; i < iterations; i++)
{
    float zx = z.x * z.x - z.y * z.y + pos.x;
    float zy = 2 * z.x * z.y + pos.y;
    r2 = zx * zx + zy * zy;
    if (r2 > N2)
    {
        n = i;
        break;
    }
    z = vec2(zx, zy);
}
return n;
}
"""

FS = """
// this vector contains the coordinates of the current pixel
// varying_tex_coords contains a position in [0,1]^2
vec2 pos = vec2(-2.0 + 3. * varying_tex_coords.x, 
                -1.5 + 3. * varying_tex_coords.y);

// run mandelbrot system
int n = mandelbrot_escape(pos, iterations);

float c = log(float(n)) / log(float(iterations));

// compute the red value as a function of n
out_color = vec4(c, 0., 0., 1.);
"""

def get_iterations(zoom=1):
    return int(500 * np.log(1 + zoom))

class MandelbrotVisual(TextureVisual):
    def initialize_fragment(self):
        self.add_fragment_header(FSH)
        self.add_fragment_main(FS)
    
    def base_mandelbrot(self, iterations=None):
        if iterations is None:
            iterations = get_iterations()
        self.add_uniform("iterations", vartype="int", ndim=1, data=iterations)
        
    def initialize(self, *args, **kwargs):
        iterations = kwargs.pop('iterations', None)
        super(MandelbrotVisual, self).initialize(*args, **kwargs)
        self.base_mandelbrot(iterations)

def update(figure, parameter):
    zoom = figure.get_processor('navigation').sx
    figure.set_data(iterations=get_iterations(zoom))
        
figure(constrain_ratio=True,
       constrain_navigation=True,)

visual(MandelbrotVisual)

# event('Pan', pan)
event('Zoom', update)

show()