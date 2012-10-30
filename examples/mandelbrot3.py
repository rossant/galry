from galry import *
import numpy as np
import numpy.random as rdn


class MandelbrotTemplate(DefaultTemplate):
    def initialize(self, **kwargs):
        
        self.set_size(4)
        self.set_rendering_options(primitive_type=PrimitiveType.TriangleStrip)
        
        points = (-1, -1, 1, 1)
        x0, y0, x1, y1 = points
        x0, x1 = min(x0, x1), max(x0, x1)
        y0, y1 = min(y0, y1), max(y0, y1)
        
        position = np.zeros((4,2))
        position[0,:] = (x0, y0)
        position[1,:] = (x1, y0)
        position[2,:] = (x0, y1)
        position[3,:] = (x1, y1)
                                
        tex_coords = np.zeros((4,2))
        tex_coords[0,:] = (0, 1)
        tex_coords[1,:] = (1, 1)
        tex_coords[2,:] = (0, 0)
        tex_coords[3,:] = (1, 0)
        
        self.add_attribute("position", vartype="float", ndim=2,
            default=position)
            
        self.add_uniform("iterations", vartype="int", ndim=1)
        
        self.add_attribute("tex_coords", vartype="float", ndim=2,
            default=tex_coords)
        self.add_varying("varying_tex_coords", vartype="float", ndim=2)
        
        
        self.add_vertex_main("""
    varying_tex_coords = tex_coords;
        """)
        
        
        self.add_fragment_header("""
// take a position and a number of iterations, and
// returns the first iteration where the system escapes a box of size N.
int mandelbrot_escape(vec2 pos, int iterations)
{
    vec2 z = vec2(0, 0);
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
        z = vec2(zx, zy);
    }
    return n;
}
        """)
        
        
        self.add_fragment_main("""
    // maximum number of iterations
    //int iterations = 100;
    
    // this vector contains the coordinates of the current pixel
    // varying_tex_coords contains a position in [0,1]^2
    vec2 pos = vec2(0, 0);
    pos.x = -2 + varying_tex_coords.x * 3;
    pos.y = -1.5 + 3 * varying_tex_coords.y;
    
    // run mandelbrot system
    int n = mandelbrot_escape(pos, iterations);
    
    // compute the red value as a function of n
    out_color.r = log(n) / log(iterations);
        """)
        
        
        
        super(MandelbrotTemplate, self).initialize(**kwargs)


class MandelbrotPaintManager(PaintManager):
    def initialize(self):
        # create the textured rectangle and specify the shaders
        self.create_dataset(MandelbrotTemplate)
        self.set_data(iterations=100)

class MandelbrotInteractionManager(InteractionManager):
    def process_zoom_event(self, event, parameter):
        super(MandelbrotInteractionManager, self).process_zoom_event(event, parameter)
        if event == InteractionEvents.ZoomEvent:
            self.paint_manager.set_data(iterations=int(300*np.log(1+self.sx)))
        
class MandelbrotWidget(GalryWidget):
    auto_zoom = QtCore.pyqtSignal(float, float, float, float)
    
    def initialize(self):
        self.constrain_ratio=True
        self.t = 0.
        self.dt = .02
        self.set_companion_classes(paint_manager=MandelbrotPaintManager,
                                    interaction_manager=MandelbrotInteractionManager)
        
    def initialized(self):
        # start simulation after initialization completes
        self.timer = QtCore.QTimer()
        self.timer.setInterval(self.dt * 1000)
        self.timer.timeout.connect(self.update)
        self.connect_events(self.auto_zoom, InteractionEvents.ZoomEvent)
        self.timer.start()
        
    def update(self):
        z = self.dt * .75
        px, py = .55903686, .38220144
        self.auto_zoom.emit(z, px, z, py)
        self.t += self.dt
        if self.t >= 13:
            self.timer.stop()
        
    def showEvent(self, e):
        # start simulation when showing window
        self.timer.start()
        
    def hideEvent(self, e):
        # stop simulation when hiding window
        self.timer.stop()
        
        
        
if __name__ == '__main__':
    print "Zoom in!"
    window = show_basic_window(widget_class=MandelbrotWidget)
    