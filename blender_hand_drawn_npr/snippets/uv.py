import imageio
from skimage import io, measure, filters, exposure
import matplotlib.pyplot as plt
import numpy as np
import os


def uv_slice(channel_img, num_segments):
    composite_img = np.zeros_like(channel_img)
    max_size = 65535
    slice_size = max_size / num_segments

    current = 0
    for i in range(0, num_segments):
        lower_slice_mask = channel_img < current
        upper_slice_mask = channel_img >= current + slice_size

        slice_mask = np.zeros_like(lower_slice_mask)
        slice_mask[lower_slice_mask] = True
        slice_mask[upper_slice_mask] = True

        if i % 2:
            mask_tone = 40000
        else:
            mask_tone = 60000
        composite_img[np.invert(slice_mask)] = mask_tone

        current += slice_size

    # Blue values are only 0 outside the object boundary, and 65535 everywhere else. Use this to create a
    # boundary mask, and apply it.
    mask = np.invert(image[:, :, 2] > 0)
    composite_img[mask] = 0

    io.imshow(composite_img)
    io.show()

    return composite_img


# image = imageio.imread("/tmp/uv_plane/UV0001.tif")
image = imageio.imread("/tmp/undulating_plane/UV0001.tif")

# Need this since tiff/png file formats will result in non-linear colourspace.
image = exposure.adjust_gamma(image, 2.2)

red_channel = image[:, :, 0]
green_channel = image[:, :, 1]

segments = 40
red_slice = uv_slice(red_channel, segments)
green_slice = uv_slice(green_channel, segments)

# imageio.imwrite("/tmp/uv_plane/uv_out.tif", composite_img)

red_contours = measure.find_contours(red_slice, 40000)
green_contours = measure.find_contours(green_slice, 40000)
all_contours = red_contours + green_contours

# Display all contours found.
fig, ax = plt.subplots()
ax.invert_yaxis()

for contour in all_contours:
    if len(contour) > 100:
        ax.plot(contour[:, 1], contour[:, 0], linewidth=1)
plt.show()
