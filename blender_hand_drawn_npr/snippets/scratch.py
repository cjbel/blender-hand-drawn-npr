from blender_hand_drawn_npr.variable_density import moving_front_nodes
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from skimage import io


class Doodah:

    def __init__(self, dir):
        self.image = io.imread(dir, as_gray=True)

    # simple function; flat everywhere, with dense point in the centre
    def density_fn(self, x, y):
        # return np.maximum(0.1, (self.image[int(round(y)), int(round(x))]) * 0.5)
        # return np.maximum(0.1, (self.image[int(round(y)), int(round(x))]) * 0.3)
        # return np.maximum(0.01, (self.image[int(round(y)), int(round(x))]) * 0.1)
        return np.maximum(0.005, ((self.image[int(round(y)), int(round(x))]) ** 4) * 0.5)


dir = 'basic_placement/DiffDir0001.png'
doodah = Doodah(dir)

# nodes = moving_front_nodes(doodah.density_fn, (500, 250, 600, 350))
nodes = moving_front_nodes(doodah.density_fn, (0, 0, 960 - 1, 540 - 1), new_pts=10)
# print(nodes)

fig = plt.figure(figsize=(14, 8))
ax1 = fig.add_subplot(1, 1, 1)

plt.rc('figure', figsize=(12.0, 12.0))

# node layout
ax1.plot(nodes[:, 0], nodes[:, 1], '.', markersize=1)
ax1.axis("image")
# ax1.set_xlim(500, 600)
# ax1.set_ylim(250, 350)
ax1.set_xlim(0, 960)
ax1.set_ylim(0, 540)
ax1.set_title("Node density")
ax1.invert_xaxis()

plt.show()