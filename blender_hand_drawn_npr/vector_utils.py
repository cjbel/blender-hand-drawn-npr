import blender_hand_drawn_npr.point_utils as point_utils

import numpy as np
import logging
import svgwrite

logger = logging.getLogger(__name__)


def create_canvas(image_file, width, height):
    """
    Create a new vector drawing.

    :param image_file: Path to output image file.
    :param width: Image width.
    :param height: Image height.
    :return: svgwrite drawing object.
    """
    logger.debug("Creating illustration canvas...")

    return svgwrite.Drawing(image_file, (width, height))


def save(drawing):
    """
    Save a vector drawing to disk.

    :param drawing: Svgwrite drawing object.
    :return: None
    """
    logger.debug("Saving illustration...")

    drawing.save()


def translate(vertices, x, y):
    """
    Translate a list of vertices by x, y.

    Ref:
    https://www.mathplanet.com/education/geometry/transformations/transformation-using-matrices

    :param vertices: List of vertices to be transformed (u, v).
    :param x: x-delta.
    :param y: y-delta.
    :return: Transformed list of vertices (u, v).
    """
    logger.debug("Vertices pre-translation: %s", vertices.tolist())

    # Unpack provided vertices into matrix form.
    v = np.matrix([[v[0] for v in vertices],
                   [v[1] for v in vertices]])

    # Define translation matrix.
    t = np.matrix([[x],
                   [y]])

    # Perform the transform.
    transform = v + t

    # Transpose the result to attain the same format as the original function argument.
    vertices = np.array(transform.T)
    logger.debug("Vertices post-translation: %s", vertices.tolist())

    return vertices


def rotate_about_xy(vertices, x, y, angle):
    """
    Rotate a list of vertices about center x, y.

    Ref:
    https://www.mathplanet.com/education/geometry/transformations/transformation-using-matrices
    https://stackoverflow.com/questions/9389453/rotation-matrix-with-center
    https://math.stackexchange.com/questions/2093314/rotation-matrix-and-of-rotation-around-a-point

    :param vertices: List of vertices to be transformed (u, v).
    :param x: x-coordinate of center of rotation.
    :param y: y-coordinate of center of rotation.
    :param angle: Angle of rotation from the horizontal (x+).
    :return: Transformed list of vertices (u, v).
    """
    logger.debug("Vertices pre-rotation: %s", vertices.tolist())

    # Define translation matrices.
    t_1 = np.matrix([[1, 0, x],
                     [0, 1, y],
                     [0, 0, 1]])
    t_2 = np.matrix([[1, 0, -x],
                     [0, 1, -y],
                     [0, 0, 1]])

    # Define rotation matrix.
    theta = np.radians(angle)
    r = np.matrix([[np.cos(theta), -np.sin(theta), 0],
                   [np.sin(theta), np.cos(theta), 0],
                   [0, 0, 1]])

    # Unpack provided vertices into matrix form.
    v = np.matrix([[v[0] for v in vertices],
                   [v[1] for v in vertices],
                   [1] * len(vertices)])

    # Perform the transform.
    transform = t_1 * r * t_2 * v

    # The last row does not contain useful data, so discard it.
    transform = transform[:-1]

    # Transpose the result to attain the same format as the original function argument.
    vertices = np.array(transform.T)
    logger.debug("Vertices post-rotation: %s", vertices.tolist())

    return vertices


def draw_straight_stroke(p0, p1, thk_factor, drawing):
    """
    Add a 2D straight stroke with rounded end-caps to the drawing.

    :param p0: Start point of the stroke, coincident with the arc center of the end-cap.
    :param p1: End point of the stroke, coincident with the arc center of the end-cap.
    :param thk_factor: Thickness scaling factor.
    :param drawing: Svgwrite drawing object.
    :return: None
    """
    logger.debug("Creating straight stroke from %s to %s", p0, p1)

    # Compute the stroke length.
    length = point_utils.euclidean_dist(p0, p1)

    # Define stroke thickness for each point. TODO: May be better to take a linear transform approach (see snippet).
    t0 = point_utils.thickness_diffdir(p0, thk_factor)
    t1 = point_utils.thickness_diffdir(p1, thk_factor)

    # Define the parameterised stroke outline.
    # With the center of the leftmost end-cap taken as (0, 0), a 2D straight stroke with rounded ends can be modelled
    # as four vertices as follows.
    vertices = np.array([[0, t0 / 2],
                         [length, t1 / 2],
                         [length, -t1 / 2],
                         [0, -t0 / 2]])

    # Translate to p0.
    vertices = translate(vertices, p0.x, p0.y)

    # Rotate around p0 to achieve final position.
    angle = point_utils.heading(p0, p1)
    vertices = rotate_about_xy(vertices, p0.x, p0.y, angle)

    # Define the basic outline properties.
    stroke_outline = drawing.path(stroke='black', stroke_width=0, fill='black')

    # Create the SVG path.
    # Top edge.
    stroke_outline.push('M', vertices[0][0], vertices[0][1])
    stroke_outline.push('L', vertices[1][0], vertices[1][1])
    # Rightmost endcap.
    stroke_outline.push('A', t1 / 2, t1 / 2, 0, 0, 0, vertices[2][0], vertices[2][1])
    # Bottom edge.
    stroke_outline.push('L', vertices[3][0], vertices[3][1])
    # Leftmost endcap.
    stroke_outline.push('A', t0 / 2, t0 / 2, 0, 0, 0, vertices[0][0], vertices[0][1])
    stroke_outline.push('Z')

    logger.debug("Adding stroke to canvas...")
    drawing.add(stroke_outline)
