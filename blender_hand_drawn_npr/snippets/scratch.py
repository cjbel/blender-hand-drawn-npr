import numpy as np
from skimage import draw

from blender_hand_drawn_npr.primitives import Path
from blender_hand_drawn_npr.models import Surface

# Describe a path which follows the internal outline of the square.
edge_path = Path([[2, 2], [3, 2], [4, 2], [5, 2], [6, 2], [7, 2],
                  [7, 3], [7, 4], [7, 5], [7, 6], [7, 7],
                  [6, 7], [5, 7], [4, 7], [3, 7], [2, 7],
                  [2, 6], [2, 5], [2, 4], [2, 3]])

# Describe a path which follows the external outline of the square.
boundary_path = Path([[1, 1], [2, 1], [3, 1], [4, 1], [5, 1], [6, 1], [7, 1], [8, 1],
                      [8, 2], [8, 3], [8, 4], [8, 5], [8, 6], [8, 7], [8, 8],
                      [7, 8], [6, 8], [5, 8], [4, 8], [3, 8], [2, 8], [1, 8],
                      [1, 7], [1, 6], [1, 5], [1, 4], [1, 3], [1, 2]])

# uv_path = Path(((4, 0), (4, 1), (4, 2), (4, 3), (4, 4), (4, 5), (4, 6), (4, 7), (4, 8), (4, 9),
#                 (5, 9), (6, 9), (7, 9), (8, 9), (9, 9),
#                 (9, 8), (9, 7), (9, 6), (9, 5), (9, 4), (9, 3), (9, 2), (9, 1), (9, 0),
#                 (8, 0), (7, 0), (6, 0), (5, 0)))

rounded = edge_path.round()
print("Rounded:  ", rounded.points)

nearest = edge_path.nearest_neighbour((11, 0))
print("Nearest:  ", nearest)

rr, cc = draw.rectangle((2, 2), (7, 7))
fake_image = np.zeros((10, 10))
fake_image[rr, cc] = 1
corners = edge_path.find_corners(image=fake_image, min_distance=2, window_size=5)
print("Corners:  ", corners)

split = edge_path.split_corners(corners)
print("Split:    ", split)

# Base the surface model on this square.
surface = Surface(obj_image=fake_image,
                  z_image=fake_image,
                  diffdir_image=fake_image,
                  norm_x_image=fake_image,
                  norm_y_image=fake_image,
                  norm_z_image=fake_image,
                  u_image=fake_image,
                  v_image=fake_image)

bumped = boundary_path.bump(surface)
print("Original: ", boundary_path.points)
print("Bumped:   ", bumped.points)

unique = bumped.remove_dupes()
print("Unique:   ", unique.points)

# Round first, then we don't worry about nearby floating point values.
unique2 = rounded.remove_dupes()
print("Unique2:  ", unique2.points)

# Create a fake UV map, gradient image with a black border and a rouge pixel
# on the isoline.
x = np.linspace(0, 1, 10)
image = np.tile(x, (10, 1))
boundary = draw.polygon_perimeter((0, 0, 9, 9), (0, 9, 9, 0))
image[boundary] = 0
image[4, 4] = 0.55

from skimage import measure
contours = measure.find_contours(image, 0.444)
print(contours)
uv_path = Path(contours[0].tolist(), is_rc=True).round()

trimmed_paths = uv_path.trim_uv(image=image, target_intensity=0.4, primary_trim_size=.1)
print("Original: ", uv_path.points)
print("UV paths:  ")
for trimmed_path in trimmed_paths:
    print(trimmed_path.points)

import matplotlib.pyplot as plt
# Display the image and plot all contours found
fig, ax = plt.subplots()
ax.imshow(image, interpolation='nearest', cmap=plt.cm.gray)
for trimmed_path in trimmed_paths:
    lines = [np.array([[point[1], point[0]] for point in trimmed_path.points])]
    for n, contour in enumerate(lines):
        ax.plot(contour[:, 1], contour[:, 0], linewidth=2)

# for n, contour in enumerate(contours):
#     ax.plot(contour[:, 1], contour[:, 0], linewidth=2)

ax.axis('image')
ax.set_xticks([])
ax.set_yticks([])
plt.show()

