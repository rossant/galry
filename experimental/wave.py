from galry import *
import numpy as np

n = 100

# normal: (df/dx, df/dy, -1)

surface(np.zeros((n, n)), vertex_shader="""
float t = ambient_light;

// convert the position from 3D to 4D.
gl_Position = vec4(position, 1.0);
float x = position.x;
float y = position.z;

float c = .1;
float d = 10;
float r = sqrt(x*x+y*y);
float u = mod(t*.5, 6.28/d);
float z = c * cos(d*(r-u));
float tmp = -d*sin(d*(r-u))*(-1/r);
float dx = tmp*x;
float dy = tmp*y;

vec3 normal2 = vec3(c*dx, 1, c*dy);
vec4 color2 = vec4((x+1)/2, (y+1)/2, (z+1)/2,1);
//color2.xyz = normal2;

gl_Position.y = z;

// compute the amount of light
float light = dot(light_direction, normalize(mat3(camera) * mat3(transform) * normal2));
//light = clamp(light, 0, 1);
light = abs(clamp(light, -1, 1));
// add the ambient term
light = clamp(.25 + light, 0, 1);

// compute the final color
varying_color = color2 * light;

// keep the transparency
varying_color.w = color2.w;
""")

def anim(fig, t):
    fig.set_data(ambient_light=t[0])

animate(anim, dt=.02)

show()
