from matplotlib import pyplot as plt

from skimage import data
from skimage.feature import corner_harris, corner_subpix, corner_peaks
from skimage.transform import warp, AffineTransform
from skimage.draw import ellipse

from blender_hand_drawn_npr.surface import Surface

surface = Surface()
surface.init_obj_image("/tmp/undulating_plane/IndexOB0001.png")

image = surface.obj_image

coords = corner_peaks(corner_harris(image), min_distance=50)  # Need to make this User configurable.
print(coords)
coords_subpix = corner_subpix(image, coords, window_size=13)
print(coords_subpix)

fig, ax = plt.subplots()
ax.imshow(image, interpolation='nearest', cmap=plt.cm.gray)
ax.plot(coords[:, 1], coords[:, 0], '.b', markersize=3)
ax.plot(coords_subpix[:, 1], coords_subpix[:, 0], '+r', markersize=15)
# ax.axis((400, 500, 150, 100))
plt.show()