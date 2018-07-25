"""
Prototype code related to S30, needs to be refactored/structured into project.
"""

import numpy as np
from skimage import feature, io, filters, img_as_uint, measure, draw, img_as_float
import rdp


def show(image):
    # TODO: Issue - doesnt always truly represent the array! Something to do with low contrast images?
    io.imshow(image)
    io.show()


def dummy_image():
    """ Generate a simple solid rectangle as an image. """
    image = np.zeros((20, 20))
    start = (5, 5)
    end = (14, 14)
    rr, cc = draw.rectangle(start, end=end, shape=image.shape)
    image[rr, cc] = 1
    return image


def read_image(image_file):
    return io.imread(image_file, as_gray=True)


def detect_edges(image):
    # return feature.canny(image, sigma=1)  # Canny doesn't work well with find_contours (too many different sets returned).
    return filters.sobel(image)


def write_image(image, image_file):
    io.imsave(image_file, image)


def path_trace(image):
    return measure.find_contours(image, .99)


def visualise_contours(contours):
    import matplotlib.pyplot as plt

    # Display the image and plot all contours found.
    fig, ax = plt.subplots()

    for n, contour in enumerate(contours):
        ax.plot(contour[:, 1], contour[:, 0], linewidth=2)

    ax.axis('image')
    ax.set_xticks([])
    ax.set_yticks([])
    plt.show()


def draw_points(coords, dim):
    """ Draw each pixel in the coord set. """
    render = np.zeros(dim)

    for coord in coords:
        render[coord[0], coord[1]] = 1

    return render


def draw_lines(coords, dim):
    """ Draw straight lines between provided coordinates. """
    render = np.zeros(dim)

    for n in range(0, len(coords) - 1):
        rr, cc = draw.line(coords[n][0], coords[n][1], coords[n + 1][0], coords[n + 1][1])
        render[rr, cc] = 1

    return render


def vectorise_image(coords, dim, image_file):
    import svgwrite

    drawing = svgwrite.Drawing(image_file, (dim[1], dim[0]))
    path = drawing.path(stroke='black', stroke_width=1, fill='none')

    for n, coord in enumerate(coords):
        if n == 0:
            path.push('M', coord[1], coord[0])
        else:
            path.push('L', coord[1], coord[0])

    drawing.add(path)
    drawing.save()


if __name__ == "__main__":
    raster_image = read_image("/tmp/img/IndexOB0001.png")
    # raster_image = dummy_image()
    show(raster_image)

    # Get the first contour group (seems good enough).
    edge_points = path_trace(raster_image)[0]

    # Convert approximations to pixel values (nearest integer).
    edge_points = np.round(edge_points).astype(np.int)

    # Optimise (Ramer-Douglas-Peucker).
    edge_points = rdp.rdp(edge_points, epsilon=1)  # Still get quite good results with this high
    raster_point_render = draw_points(edge_points, raster_image.shape)
    show(raster_point_render)

    raster_render = draw_lines(edge_points, raster_image.shape)
    write_image(raster_render, "/tmp/img/out.png")
    show(raster_render)

    vectorise_image(edge_points, raster_image.shape, "/tmp/img/out.svg")
