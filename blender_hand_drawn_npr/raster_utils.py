import logging
from skimage import io, measure, filters, exposure
import imageio
import numpy as np

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


def path_trace(image, threshold=0):
    """
    Detect contours of white boundaries.

    :param image: Numpy ndarray.
    :param threshold: Acceptance threshold. Contours of length below this value will be considered invalid and rejected.
    :return: List of contours.
    """
    contours = measure.find_contours(image, .99)

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

    for stepwise_slice in range(0, num_slices, 2):
        logger.debug("Computing slice %d...", stepwise_slice)

        start_boundary = stepwise_slice * slice_size
        logger.debug("Start boundary: %f", start_boundary)

        end_boundary = start_boundary + slice_size
        logger.debug("End boundary: %f", end_boundary)

        start_boundary_mask = image < start_boundary
        end_boundary_mask = image >= start_boundary + slice_size

        stepwise_slicemask = np.zeros_like(start_boundary_mask)
        stepwise_slicemask[start_boundary_mask] = True
        stepwise_slicemask[end_boundary_mask] = True

        slicemask[np.invert(stepwise_slicemask)] = True

    return slicemask
