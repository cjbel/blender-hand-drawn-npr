from blender_hand_drawn_npr.models import Surface
import os
import matplotlib.pyplot as plt
import numpy as np
from skimage import filters, feature, io, util, segmentation, measure, color, transform
from scipy import stats
import matplotlib.patches as mpatches

surface = Surface()
img_dir = "/tmp/test"
img_dir = "/tmp/"
img_dir = "/tmp/undulating_plane2"
surface.init_obj_image(os.path.join(img_dir, "IndexOB0001.png"))
surface.init_z_image(os.path.join(img_dir, "Depth0001.png"))
# surface.init_diffdir_image(os.path.join(img_dir, "DiffDir0001.png"))
surface.init_norm_image(os.path.join(img_dir, "Normal0001.tif"))
surface.init_uv_image(os.path.join(img_dir, "UV0001.tif"))
# surface.init_shadow_image(os.path.join(img_dir, "Shadow0001.png"))
# surface.init_ao_image(os.path.join(img_dir, "AO0001.png"))

mask = surface.obj_image
sobel_norm = filters.sobel(image=color.rgb2gray(surface.norm_image), mask=mask)
sobel_z = filters.sobel(image=surface.z_image, mask=mask)

# image = sobel_z
# image = sobel_norm
image = sobel_norm + sobel_z

# image = filters.gaussian(image, sigma=4)

nonzero_idx = np.nonzero(image)
vals = image[nonzero_idx]

percentile = np.percentile(vals, 99)

image = image > percentile
io.imshow(image)
io.show()

lines = transform.probabilistic_hough_line(image, threshold=100, line_length=20,
                                           line_gap=100)
print(len(lines))

# Display the image and plot all contours found
fig, ax = plt.subplots()
ax.imshow(surface.z_image, interpolation='nearest', cmap=plt.cm.gray)
for line in lines:
        p0, p1 = line
        ax.plot((p0[0], p1[0]), (p0[1], p1[1]))
ax.axis('image')
ax.set_xticks([])
ax.set_yticks([])
plt.show()

label_image = measure.label(image)
image_label_overlay = color.label2rgb(label_image, image=image)
io.imshow(image_label_overlay)
io.show()

fig, ax = plt.subplots(figsize=(10, 6))
ax.imshow(image_label_overlay)
for region in measure.regionprops(label_image):
    # if region.mean_intensity > 0.8:
    #     print("##")
    if region.area >= 100:
        # draw rectangle around segmented coins
        minr, minc, maxr, maxc = region.bbox
        rect = mpatches.Rectangle((minc, minr), maxc - minc, maxr - minr,
                                  fill=False, edgecolor='red', linewidth=2)
        ax.add_patch(rect)

ax.set_axis_off()
plt.tight_layout()
plt.show()

io.imshow(measure.regionprops(label_image)[0].image)
io.show()

contours = measure.find_contours(measure.regionprops(label_image)[0].image, 0.99)
print(contours)

# contours = measure.find_contours(image, level=0.99)
#
# Display the image and plot all contours found
fig, ax = plt.subplots()
ax.imshow(image, interpolation='nearest', cmap=plt.cm.gray)
for n, contour in enumerate(contours):
    ax.plot(contour[:, 1], contour[:, 0], linewidth=2)
ax.axis('image')
ax.set_xticks([])
ax.set_yticks([])
plt.show()
#
# init = contours[0]
# snake = segmentation.active_contour(image, init, bc="fixed", w_edge=1)
#
# # Display the image and plot all contours found
# fig, ax = plt.subplots()
# # ax.imshow(surface.z_image, interpolation='nearest', cmap=plt.cm.gray)
# ax.plot(snake[:, 1], snake[:, 0], linewidth=2)
# ax.axis('image')
# ax.set_xticks([])
# ax.set_yticks([])
# plt.show()
