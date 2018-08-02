import blender_hand_drawn_npr.point_utils as point_utils

import logging
from skimage import io, measure, filters, exposure
import imageio
import numpy as np
from collections import namedtuple
import matplotlib.pyplot as plt

logger = logging.getLogger(__name__)


def read_gray_image(image_file):
    """
    Read a raster image from disk as grayscale.

    :param image_file: Path to image file.
    :return: Numpy ndarray.
    """
    logger.debug("Reading grayscale raster image file from disk: %s", image_file)

    return io.imread(image_file, as_gray=True)


def write_raster_image(image, image_file):
    """
    Write a raster image to disk.

    :param image: Numpy ndarray.
    :param image_file: Path to image file.
    :return: None
    """
    logger.debug("Writing raster image file to disk: %s", image_file)

    io.imsave(image_file, image)


def detect_edges(image):
    """
    Apply an edge detection algorithm to an image.

    :param image: Numpy ndarray.
    :return: Numpy ndarray.
    """
    return filters.sobel(image)


def path_trace(image, intensity=0.99, threshold=0):
    """
    Detect contours of boundaries.

    :param intensity: Isovalue.
    :param image: Numpy ndarray.
    :param threshold: Acceptance threshold. Contours of length below this value will be considered invalid and rejected.
    :return: List of contours.
    """
    contours = measure.find_contours(image, intensity)

    # Reject contours whose lengths are below the acceptance threshold.
    valid_contours = []
    for contour in contours:
        contour_len = len(contour)
        if contour_len < threshold:
            logger.debug("Contour of length %d rejected.", contour_len)
        else:
            valid_contours.append(contour)

    logger.debug("Valid contour sets found: %d", len(valid_contours))

    return valid_contours


def min_max_rgb(image):
    min = (image[:, :, 0].min(),
           image[:, :, 1].min(),
           image[:, :, 2].min())

    max = (image[:, :, 0].max(),
           image[:, :, 1].max(),
           image[:, :, 2].max())

    logger.debug("Min/Max RGB values: %s, %s", min, max)

    return min, max


def linearise_colourspace(image):
    logger.debug("Linearising colorspace...")

    return exposure.adjust_gamma(image, 2.2)


def read_rgb_image(image_file):
    logger.debug("Reading RGB raster image file from disk: %s", image_file)

    return imageio.imread(image_file)


def image_to_components(image):
    return image[:, :, 0], image[:, :, 1]


def trim_streamline(streamline, intensity, u_threshold, v_threshold, uv_image, direction):

    u_image, v_image = image_to_components(uv_image)

    trimmed_streamline = []
    if direction == 'u':
        for point in streamline:
            if (intensity - u_threshold) <= point.u <= (intensity + u_threshold) and \
                    (v_image.min() + v_threshold) <= point.v <= (v_image.max() - v_threshold):
                trimmed_streamline.append(point)

    elif direction == 'v':
        for point in streamline:
            if (intensity - v_threshold) <= point.v <= (intensity + v_threshold) and \
                    (u_image.min() + u_threshold) <= point.u <= (u_image.max() - u_threshold):
                trimmed_streamline.append(point)

    else:
        raise ValueError("direction argument must be equal to 'u' or 'v'")

    return trimmed_streamline


def uv_streamlines(u_slices, u_threshold, v_slices, v_threshold, render_pass):
    # Tiff/png file formats are mapped to a non-linear colourspace, which skew the uv coords. Transform to linear
    # colorspace.
    u_image, v_image = image_to_components(render_pass.uv)
    u_grid_width, v_grid_width = (u_image.max() - u_image.min()) / u_slices, \
                                (v_image.max() - v_image.min()) / v_slices

    # Identify u and v intensity values representing each slice boundary.
    u_intensities = []
    for streamline_pos in range(1, u_slices):
        u_intensities.append(streamline_pos * u_grid_width)

    v_intensities = []
    for streamline_pos in range(1, v_slices):
        v_intensities.append(streamline_pos * v_grid_width)

    # Compute u and v streamlines.
    u_streamlines = []
    for intensity in u_intensities:
        streamline_coords = path_trace(image=u_image,
                                       intensity=intensity)[0]
        streamline = point_utils.coords_to_points(streamline_coords,
                                                  render_pass=render_pass)
        streamline = point_utils.remove_duplicate_coords(streamline)
        streamline = trim_streamline(streamline=streamline,
                                     intensity=intensity,
                                     u_threshold=u_threshold,
                                     v_threshold=v_threshold,
                                     uv_image=render_pass.uv,
                                     direction="u")
        streamline = point_utils.optimise_path(streamline, 10)  # TODO: Make factor user configurable
        u_streamlines.append(streamline)

    v_streamlines = []
    for intensity in v_intensities:
        streamline_coords = path_trace(image=v_image,
                                       intensity=intensity)[0]
        streamline = point_utils.coords_to_points(streamline_coords,
                                                  render_pass=render_pass)
        streamline = point_utils.remove_duplicate_coords(streamline)
        streamline = trim_streamline(streamline=streamline,
                                     intensity=intensity,
                                     u_threshold=u_threshold,
                                     v_threshold=v_threshold,
                                     uv_image=render_pass.uv,
                                     direction="v")
        streamline = point_utils.optimise_path(streamline, 10)  # TODO: Make factor user configurable
        v_streamlines.append(streamline)

    return u_streamlines, v_streamlines
