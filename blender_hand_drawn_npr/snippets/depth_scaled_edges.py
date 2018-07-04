"""
Preliminary requirement: Line thickness should be proportional to the distance of the pixel from the camera.

This is a possible implementation which operates as follows:
    - Canny image filter produces a binary image with edges represented as white pixels. All edges are 1-pixel wide.
    - For each of these "edge pixels":
        - Establish depth from the corresponding depth map.
        - In a separate image, draw a circle with centre corresponding to the edge pixel location, of a radius
        proportional to its depth.
    - Convert the resulting raster image to vector.

    Given the gradual nature of depth transitions between neighbouring pixels, this approach generates edges which
    appear to smoothly taper as they travel away from the camera position.
"""

import os
from subprocess import run

import numpy as np
from skimage import io, feature, img_as_uint, draw

img_file_root = 'blend_files/img/'

# Load the depth map as a greyscale image.
depth_map_filename = 'Depth0001.png'
depth_map = io.imread(os.path.join(img_file_root, depth_map_filename), as_grey=True)

# Find edges. Canny will yield a binary image, True (white) pixels are edge pixels.
# TODO: Sigma may need tuned, need to look at a broader range of geometry. Too large a value appears to perturb the edge
# line away from the original image, creating issues when querying the depth on an edge.
edge_map = feature.canny(depth_map, sigma=1)

# Save to disk for debugging.
edge_map_filename = 'Edge.bmp'
io.imsave(os.path.join(img_file_root, edge_map_filename), img_as_uint(edge_map))

# Define an empty array to contain our scaled edges.
scaled_edge_map = np.zeros((len(edge_map), len(edge_map[0])))

# TODO: We need to visit each edge pixel in the 2D array. Most pixels will not be an edge pixel however, so iterating
# over the whole array is inefficient, but fine for proof-of-concept.
for y_coord, row in enumerate(edge_map):
    for x_coord, col in enumerate(row):
        # Each cell in a greyscale row array holds a single value, so the col is actually just the pixel value.
        pixel = col
        # Test whether the pixel is an edge pixel.
        if pixel:
            # Read the depth at the corresponding location in the depth map.
            # TODO: The edge map generally corresponds well (pixel-by-pixel) to the depth map, but not always.
            # E.g. If an edge map pixel lies outside the depth map, a "distant" value will be returned. This is probably
            # why some areas of the output are rendered with conspicuous slim lines.
            depth = depth_map[y_coord][x_coord]

            # Depth scaling characteristics.
            min_depth = np.amin(depth_map)  # Per normalised depth map.
            max_depth = np.amax(depth_map)  # Per normalised depth map.
            min_thickness = 1  # User can specify this. A line thickness of 1-pixel is the lowest practical value.
            max_thickness = 20  # User can specify this.

            # We want low depth values to correspond to high thickness values and vice versa. Compute the thickness by
            # linear transform.
            edge_thickness = (((depth - min_depth) / (max_depth - min_depth)) * (
                    min_thickness - max_thickness)) + max_thickness

            # Define a circle centred on this location.
            radius = edge_thickness / 2
            y_coords, x_coords = draw.circle(y_coord, x_coord, radius)

            # Draw the circle's pixels as white at the corresponding centre in our separate array.
            scaled_edge_map[y_coords, x_coords] = 1

# Save output as bitmap.
scaled_edge_filename = 'Scaled_Edge.bmp'
io.imsave(os.path.join(img_file_root, scaled_edge_filename), img_as_uint(scaled_edge_map))

# Finally, convert to vector.
run(['potrace', '--svg', os.path.join(img_file_root, scaled_edge_filename)])
