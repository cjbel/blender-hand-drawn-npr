from skimage import io, measure
import rdp


def read_image(image_file):
    """
    Read a raster image from disk as grayscale.

    :param image_file: Path to image file.
    :return: Numpy ndarray.
    """
    return io.imread(image_file, as_gray=True)


def write_raster_image(image, image_file):
    """
    Write a raster image to disk.

    :param image: Numpy ndarray.
    :param image_file: Path to image file.
    :return: None
    """
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
    return measure.find_contours(image, .99)


def coord_linear_optimise(coord_list):
    """
    Simplify a list of coordinates whilst maintaining the overall shape of the path they represent.

    :param coord_list: List of Points.
    :return: Optimised list of Points.
    """
    return rdp.rdp(coord_list, epsilon=1)

