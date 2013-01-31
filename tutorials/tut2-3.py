"""Tutorial 2.3: Convay's Game of Life.

In this tutorial, we show how to simulate the Convay's Game of Life
by animating a texture at regular intervals.

"""

from galry import *
from numpy import *

# Grid size.
size = 64

# We define the function used to update the system. The system is defined
# as a matrix with 0s (dead cells) and 1s (alive cells).
def iterate(Z):
    """Perform an iteration of the system."""
    # code from http://dana.loria.fr/doc/numpy-to-dana.html
    # find number of neighbours that each square has
    N = zeros(Z.shape)
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

# We define the update function which updates the texture and legend text
# at every iteration.
def update(figure, parameter):
    """Update the figure at every iteration."""
    # We initialize the iteration to 0 at the beginning.
    if not hasattr(figure, 'iteration'):
        figure.iteration = 0
    # We iterate the matrix.
    mat[:,:,0] = iterate(mat[:,:,0])
    # We update the texture and the iteration text.
    figure.set_data(texture=mat, visual='image')
    figure.set_data(text="Iteration %d" % figure.iteration, visual='iteration')
    figure.iteration += 1

# We create a figure with constrained ratio and navigation.
figure(constrain_ratio=True, constrain_navigation=True,)

# We create the initial matrix with random values, and we only update the 
# red channel.
mat = zeros((size, size, 3))
mat[:,:,0] = random.rand(size,size) < .2

# We show the image.
imshow(mat, name='image')

# We show the iteration text at the top.
text(fontsize=18, name='iteration', text='Iteration',
    coordinates=(0., .95), is_static=True)

# We animate the figure, with the update function called every 0.05 seconds
# (i.e. 20 FPS).
animate(update, dt=.05)

show()
