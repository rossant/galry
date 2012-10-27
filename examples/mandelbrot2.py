from galry import *
import numpy as np
import numpy.random as rdn

# Vertex shader
VS = """
%AUTODECLARATIONS%

void main()
{
    // transform position
    gl_Position = gl_ModelViewProjectionMatrix * position;
    
    // pass the texture coordinate to the fragment shader
    // this vec2 contains the (x, y) coordinates of the current vertex
    gl_TexCoord[0] = texture_coordinates;
}
"""

# Fragment shader
FS = """
// take a position and a number of iterations, and
// returns the first iteration where the system escapes a box of size N.
int mandelbrot_escape(vec2 pos, int iterations)
{
    vec2 z = vec2(0., 0.);
    int n = 0;
    int N = 10;
    int N2 = N * N;
    float r2;
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
        z.x = zx;
        z.y = zy;
    }
    return n;
}

uniform int iterations;

// main program
void main()
{
    // maximum number of iterations
    //int iterations = 100;
    
    // this vector contains the coordinates of the current pixel
    // gl_TexCoord[0] contains a position in [0,1]^2
    vec2 pos;
    pos.x = -2 + gl_TexCoord[0].x * 3;
    pos.y = -1.5 + 3 * gl_TexCoord[0].y;
    
    // run mandelbrot system
    int n = mandelbrot_escape(pos, iterations);
    
    // compute the red value as a function of n
    gl_FragColor.r = log(n) / log(iterations);
}
"""

# empty texture, the size does not matter since all pixels are updated
# in the fragment shader
texture = np.zeros((2, 2, 3))

class MandelbrotPaintManager(PaintManager):
    def initialize(self):
        # create the textured rectangle and specify the shaders
        self.add_textured_rectangle(texture, vertex_shader=VS,
                                    fragment_shader=FS, iterations=100)
                              
class MandelbrotInteractionManager(InteractionManager):
    def process_zoom_event(self, event, parameter):
        super(MandelbrotInteractionManager, self).process_zoom_event(event, parameter)
        if event == InteractionEvents.ZoomEvent:
            self.paint_manager.update_uniform_values(iterations=int(100*np.log(1+self.sx)))
        
if __name__ == '__main__':
    print "Zoom in!"
    window = show_basic_window(paint_manager=MandelbrotPaintManager,
                               interaction_manager=MandelbrotInteractionManager,
                               constrain_ratio=True)
    