import logging
from skimage import io, measure, filters
import rdp


logger = logging.getLogger(__name__)


def read_image(image_file):
    """
    Read a raster image from disk as grayscale.

    :param image_file: Path to image file.
    :return: Numpy ndarray.
    """
    logger.debug("Reading raster image file from disk: %s", image_file)

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


def path_trace(image):
    """
    Detect contours of white boundaries.

    :param image: Numpy ndarray.
    :return: List of contours.
    """
    contours = measure.find_contours(image, .99)
    logger.debug("Contour sets found: %d", len(contours))

    return contours


def coord_linear_optimise(unoptimised_coords):
    """
    Simplify a list of coordinates whilst maintaining the overall shape of the path they represent.

    :param unoptimised_coords: List of coords.
    :return: Optimised list of coords.
    """
    logger.debug("Unoptimised vertex count: %d", len(unoptimised_coords))

    optimised_coords = rdp.rdp(unoptimised_coords, epsilon=1)
    logger.debug("Optimised vertex count: %d", len(optimised_coords))

    return optimised_coords
