import numpy as np
import numpy.random as rdn
import timeit
from galry import *

# grid size
size = 64

def iterate(Z):
    # code from http://dana.loria.fr/doc/numpy-to-dana.html
    # find number of neighbours that each square has
    N = np.zeros(Z.shape)
    N[1:, 1:] += Z[:-1, :-1]
    N[1:, :-1] += Z[:-1, 1:]
    N[:-1, 1:] += Z[1:, :-1]
    N[:-1, :-1] += Z[1:, 1:]
    N[:-1, :] += Z[1:, :]
    N[1:, :] += Z[:-1, :]
    N[:, :-1] += Z[:, 1:]
    N[:, 1:] += Z[:, :-1]
    # a live cell is killed if it has fewer than 2 or more than 3 neighbours.
    part1 = ((Z == 1) & (N < 4) & (N > 1))
    # a new cell forms if a square has exactly three members
    part2 = ((Z == 0) & (N == 3))
    Z = (part1 | part2).astype(int)
    return Z
    
class ConwayPaintManager(PaintManager):
    def get_iteration_text(self):
        return "Iteration %05d" % self.iteration
        
    def initialize(self):
        # initial data
        self.data = np.zeros((size,size,3), dtype=np.float32)
        self.data[:,:,0] = rdn.rand(size,size)<.2
        # create textured rectangle
        self.add_visual(TextureVisual, texture=self.data)
        # iteration text
        self.iteration = 0
        text = self.get_iteration_text()
        self.add_visual(TextVisual, fontsize=18, name='iteration',
            text=text, coordinates=(0., .95), is_static=True)
        
    def update_callback(self):
        self.data[:,:,0] = iterate(self.data[:,:,0])
        self.set_data(tex_sampler=self.data)
        self.set_data(text=self.get_iteration_text(), visual='iteration')
        self.iteration += 1
        
if __name__ == '__main__':
    # create window
    window = show_basic_window(paint_manager=ConwayPaintManager,
                               constrain_ratio=True,
                               constrain_navigation=True,
                               update_interval=.05)