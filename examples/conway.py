import numpy as np
import numpy.random as rdn
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
    def initialize(self):
        # initial data
        self.data = np.zeros((size,size,3), dtype=np.float32)
        self.data[:,:,0] = rdn.rand(size,size)<.2
        # create textured rectangle
        # self.texture = self.add_textured_rectangle(self.data)
        self.create_dataset(TextureTemplate, shape=self.data.shape[:2], ncomponents=3)
        self.set_data(tex_sampler=self.data)
        # iteration text
        self.iteration = 0
        text = "Iteration %04d" % self.iteration
        # TODO: bug with several textures
        # self.it = self.create_dataset(TextTemplate, text=text)
        # self.add_permanent_overlay("text", lambda: "Iteration %04d" % self.iteration, (0, .95))
        
    def update(self):
        # update the data
        self.data[:,:,0] = iterate(self.data[:,:,0])
        self.set_data(tex_sampler=self.data, dataset=self.it)
        # update the texture
        # self.update_texture(self.texture, self.data)
        # update rendering
        self.updateGL()
        self.iteration += 1
        
class ConwayPlot(GalryWidget):
    def initialize(self):
        # set custom paint manager
        self.set_companion_classes(paint_manager=ConwayPaintManager)
        self.initialize_companion_classes()
        # constrain ratio
        self.constrain_ratio = True
    
    def initialized(self):
        # start simulation after initialization completes
        self.timer = QtCore.QTimer()
        # 50 ms per iteration
        self.timer.setInterval(50)
        self.timer.timeout.connect(self.paint_manager.update)
        self.timer.start()
        
    def hideEvent(self, e):
        # stop simulation when hiding window
        self.timer.stop()

if __name__ == '__main__':
    # create window
    window = show_basic_window(ConwayPlot)