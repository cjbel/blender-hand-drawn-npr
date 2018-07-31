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


def uv_slicemask(image, min_intensity, max_intensity, num_slices):
    logger.debug("UV slices: %d", num_slices)

    interval = max_intensity - min_intensity
    logger.debug("UV slice interval: %f", interval)

    slice_size = interval / num_slices
    logger.debug("UV slice size: %f", slice_size)

    slicemask = np.zeros_like(image)

    boundaries = []

    for stepwise_slice in range(0, num_slices, 2):
        logger.debug("Computing slice %d...", stepwise_slice)

        start_boundary = stepwise_slice * slice_size
        boundaries.append(start_boundary)
        logger.debug("Start boundary: %f", start_boundary)

        end_boundary = start_boundary + slice_size
        boundaries.append(end_boundary)
        logger.debug("End boundary: %f", end_boundary)

        start_boundary_mask = image < start_boundary
        end_boundary_mask = image >= start_boundary + slice_size

        stepwise_slicemask = np.zeros_like(start_boundary_mask)
        stepwise_slicemask[start_boundary_mask] = True
        stepwise_slicemask[end_boundary_mask] = True

        slicemask[np.invert(stepwise_slicemask)] = True

    return slicemask, boundaries


def uv_streamlines(num_slices, depth_image, diffdir_image, uv_image):
    # Tiff/png file formats are mapped to a non-linear colourspace, which skew the uv coords. Transform to linear
    # colorspace.
    corrected_uv_image = linearise_colourspace(uv_image)

    UVImage = namedtuple("UVImage", "u v")
    # Split the composite uv image into their u (red) and v (green) component images.
    uv_image = UVImage(corrected_uv_image[:, :, 0], corrected_uv_image[:, :, 1])

    GridWidth = namedtuple("GridWidth", "u v")
    grid_width = GridWidth((uv_image.u.max() - uv_image.u.min()) / num_slices,
                           (uv_image.v.max() - uv_image.v.min()) / num_slices)

    u_intensities = []
    v_intensities = []
    for line_num in range(1, num_slices):
        u_intensities.append(line_num * grid_width.u)
        v_intensities.append(line_num * grid_width.v)

    raster_image = np.zeros_like(depth_image)

    u_streamlines = []
    v_streamlines = []
    for intensity in u_intensities:

        streamline = []

        contour = path_trace(image=uv_image.u,
                             intensity=intensity)[0]

        contour_points = point_utils.coords_to_points(contour,
                                                      diffdir_image=diffdir_image,
                                                      depth_image=depth_image,
                                                      uv_image=corrected_uv_image)
        contour_points = point_utils.remove_duplicate_coords(contour_points)

        u_threshold = 100  # TODO: Make User configurable.
        v_threshold = 100  # TODO: Make User configurable.
        for contour_point in contour_points:
            if (intensity - u_threshold) <= contour_point.u <= (intensity + u_threshold):
                if (uv_image.v.min() + v_threshold) <= contour_point.v <= (uv_image.v.max() - v_threshold):
                    streamline.append(contour_point)
                    raster_image[contour_point.y, contour_point.x] = 1

        streamline = point_utils.linear_optimise(streamline)

        u_streamlines.append(streamline)

    for intensity in v_intensities:

        streamline = []

        contour = path_trace(image=uv_image.v,
                             intensity=intensity)[0]

        contour_points = point_utils.coords_to_points(contour,
                                                      diffdir_image=diffdir_image,
                                                      depth_image=depth_image,
                                                      uv_image=corrected_uv_image)
        contour_points = point_utils.remove_duplicate_coords(contour_points)

        u_threshold = 100  # TODO: Make User configurable.
        v_threshold = 100  # TODO: Make User configurable.
        for contour_point in contour_points:
            if (intensity - v_threshold) <= contour_point.v <= (intensity + v_threshold):
                if (uv_image.u.min() + u_threshold) <= contour_point.u <= (uv_image.u.max() - u_threshold):
                    streamline.append(contour_point)
                    raster_image[contour_point.y, contour_point.x] = 1

        streamline = point_utils.linear_optimise(streamline)

        v_streamlines.append(streamline)

    io.imsave("/tmp/test.png", raster_image)

    return u_streamlines, v_streamlines
