from blender_hand_drawn_npr.models import Surface
import os
import matplotlib.pyplot as plt
import numpy as np
from skimage import filters, feature, io, util, segmentation, measure, color, transform, morphology, graph
from scipy import stats, ndimage
import matplotlib.patches as mpatches

# img_dir = "/tmp/test"
# img_dir = "/tmp/hyperbolic_paraboloid_xy"
# img_dir = "/tmp/undulating_plane2"
# img_dir = "/tmp/human"

surface = Surface()
surface.init_obj_image(os.path.join(img_dir, "IndexOB0001.png"))
surface.init_z_image(os.path.join(img_dir, "Depth0001.png"))

# By using the object image as a mask we find only internal edges and disregard silhouette edges.
edge_image = feature.canny(surface.z_image, sigma=1, mask=surface.obj_image.astype(bool))
io.imshow(edge_image)
io.show()

# Identify all continuous lines.
labels = measure.label(edge_image, connectivity=2)

# Plot the discovered regions.
image_label_overlay = color.label2rgb(labels, image=edge_image)
fig, ax = plt.subplots(figsize=(10, 6))
ax.imshow(image_label_overlay)
for region in measure.regionprops(labels):
    minr, minc, maxr, maxc = region.bbox
    rect = mpatches.Rectangle((minc, minr), maxc - minc, maxr - minr,
                              fill=False, edgecolor='yellow', linewidth=0.25)
    ax.add_patch(rect)
ax.set_axis_off()
plt.tight_layout()
plt.show()

routes = []
for region in measure.regionprops(labels):
    image = region.image
    # Condition the line to ensure each cell has only one or two neighbours (remove "L"s).
    image = morphology.skeletonize(image)

    # A cell with only one neighbour can be considered as the end of a continuous line, i.e
    # the sum of a cell's 8 surrounding neighbours will equal 1.
    kernel = [[1, 1, 1],
              [1, 0, 1],
              [1, 1, 1]]
    convolved = ndimage.convolve(image.astype(float), kernel, mode="constant")
    # Refine the convolution to only contain cells which were present in the original image.
    convolved[util.invert(image)] = 0

    # Extract the region coordinates of cells which meet the condition for being a start/end position.
    terminator_pair = np.argwhere(convolved == 1)
    if not len(terminator_pair):
        continue

    # Make edges have a value of 0 ("cheap").
    image = util.invert(image)

    # An ordered list of coordinates for each line is now found by computing the cheapest route between each
    # terminator_pair.
    route, cost = graph.route_through_array(image, terminator_pair[0], terminator_pair[1])
    if len(route) < 10:
        print("Route length rejected: ", str(len(route)))
        continue

    route = np.array(route)  # Conversion needed only for plotting.

    # Convert regional route coords back to global coords.
    region_offset = [region.bbox[0], region.bbox[1]]
    routes.append(route + region_offset)

fig, ax = plt.subplots()
ax.imshow(surface.z_image, interpolation='nearest', cmap=plt.cm.gray)
for route in np.array(routes):
    ax.plot(route[:, 1], route[:, 0], linewidth=2)
ax.axis('image')
ax.set_xticks([])
ax.set_yticks([])
plt.show()
