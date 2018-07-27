"""
Prototype code related to S30, needs to be refactored/structured into project.
"""

import numpy as np
from skimage import feature, io, filters, img_as_uint, measure, draw, img_as_float
import rdp
import splipy
from svgpathtools import parse_path, wsvg
import svgwrite
import math
from collections import namedtuple
import scipy
import point_utils


def draw_straight_vector_stroke(p0, p1, thk_factor):

    # Define the basic outline properties.
    stroke_outline = drawing.path(stroke='black', stroke_width=0, fill='black')

    # Compute the Euclidean distance between points, yielding stroke length.
    length = euclidean_dist(p0, p1)

    # Define stroke thickness for each point. TODO: May be better to take a linear transform approach (see snippet).
    t0 = thickness_diffdir(p0, thk_factor)
    t1 = thickness_diffdir(p1, thk_factor)

    # Define the stroke outline.
    stroke_outline.push('M', 0, 0)
    stroke_outline.push('L', length, 0)
    stroke_outline.push('A', t1 / 2, t1 / 2, 0, 1, 1, length, t1)
    stroke_outline.push('L', 0, t0)
    stroke_outline.push('A', t0 / 2, t0 / 2, 0, 1, 1, 0, 0)
    stroke_outline.push('Z')

    # Translation.
    x_trans = p0.x
    y_trans = p0.y - t0 / 2
    stroke_outline.translate(x_trans, y_trans)

    # Rotation.
    angle = heading(p0, p1)
    stroke_outline.rotate(angle, (0, t0 / 2))  # Center of rotation is relative to the original (0, 0).

    drawing.add(stroke_outline)


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


def to_svg_path(coords):
    import svgwrite

    drawing = svgwrite.Drawing("/tmp/img/dummy.svg", (99999, 99999))
    path = drawing.path(stroke='black', stroke_width=1, fill='none')

    for n, coord in enumerate(coords):
        if n == 0:
            path.push('M', coord[1], coord[0])
        else:
            path.push('L', coord[1], coord[0])

    return path.commands


def offset_curve(path, offset_distance, steps=10):
    from svgpathtools import Line, Path

    """Takes in a Path object, `path`, and a distance,
    `offset_distance`, and outputs an piecewise-linear approximation
    of the 'parallel' offset curve."""
    # Ref (verbatim): https://github.com/mathandy/svgpathtools#compatibility-notes-for-users-of-svgpath-v20
    nls = []
    for seg in path:
        for k in range(steps):
            t = k / float(steps)
            offset_vector = offset_distance * seg.normal(t)
            nl = Line(seg.point(t), seg.point(t) + offset_vector)
            nls.append(nl)
    connect_the_dots = [Line(nls[k].end, nls[k + 1].end) for k in range(len(nls) - 1)]
    if path.isclosed():
        connect_the_dots.append(Line(nls[-1].end, nls[0].end))
    offset_path = Path(*connect_the_dots)

    return offset_path


if __name__ == "__main__":

    # Define domain objects.
    Point = namedtuple("Point", "x y depth_intensity diffdir_intensity")

    object_image = read_image("/tmp/img/IndexOB0001.png")
    # depth_image = read_image("/tmp/img/Depth0001.png")
    depth_image = read_image("/tmp/img/Depth0001NORM.png")
    diffdir_image = read_image("/tmp/img/DiffDir0001.png")
    # object_image = dummy_image()
    show(object_image)

    # Get the first contour group (seems good enough).
    edge_coords = path_trace(object_image)[0]
    # # Convert approximations to pixel values (nearest integer).
    edge_coords = np.round(edge_coords).astype(np.int)

    # Optimise points (Ramer-Douglas-Peucker).
    edge_coords = rdp.rdp(edge_coords, epsilon=1)  # Still get quite good results with this high.

    # Create a list of unique Points, preserving the original order.
    points = []
    seen = set()
    for coord in edge_coords:
        r, c = coord[0], coord[1]
        if (r, c) not in seen:
            seen.add((r, c))

            depth_intensity = depth_image[r, c]
            diffdir_intensity = diffdir_image[r, c]
            point = Point(c, r, depth_intensity, diffdir_intensity)
            points.append(point)

    # Prepare the vector canvas.
    drawing = svgwrite.Drawing("/tmp/img/vector_rendering.svg", (object_image.shape[1], object_image.shape[0]))

    # Define thickness factor.
    f = 2

    # Create vector strokes.
    for i in range(0, len(points)):
        if i != len(points) - 1:
            # Draw a Stroke between adjacent Points.
            draw_straight_vector_stroke(points[i], points[i + 1], f)
        else:
            # Draw a Stroke back to the original Point to close the path.
            draw_straight_vector_stroke(points[i], points[0], f)

    drawing.save()
