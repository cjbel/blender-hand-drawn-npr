import imageio
from skimage import io, measure, filters
import matplotlib.pyplot as plt
import numpy as np

image = np.zeros((11, 11))
# Point is 0.6.
image[5, 5] = 0.6

io.imshow(image)
io.show()

# Everything above 0.5 will be exposed. This will expose the Point, masking everything else.
expose = image > 0.5

io.imshow(expose)
io.show()

# Exposed pixels get assigned 0.2. This will reshade the Point to 0.2.
image[expose] = 0.2

io.imshow(image)
io.show()