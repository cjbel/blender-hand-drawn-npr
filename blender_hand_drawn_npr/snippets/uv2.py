import imageio
from skimage import io, measure, filters, exposure
import matplotlib.pyplot as plt
import numpy as np

image = imageio.imread("/tmp/undulating_plane/UV0001.tif")
image = exposure.adjust_gamma(image, 2.2)

set_a = measure.find_contours(image[:, :, 0], 0)

set_b = measure.find_contours(image[:, :, 0], 20000)
all_contours = set_a + set_b

print(set_b[0][0])
print(set_b[0][-1])

# Display all contours found.
fig, ax = plt.subplots()
ax.invert_yaxis()

for n, contour in enumerate(all_contours):
    ax.plot(contour[:, 1], contour[:, 0], linewidth=1)
plt.show()
