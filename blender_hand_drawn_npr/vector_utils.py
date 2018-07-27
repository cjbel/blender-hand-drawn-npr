import svgwrite
import blender_hand_drawn_npr.point_utils as point_utils
import numpy as np


def create(image_file, width, height):
    """
    Create a new vector drawing.

    :param image_file: Path to output image file.
    :param width: Image width.
    :param height: Image height.
    :return: svgwrite drawing object.
    """
    return svgwrite.Drawing(image_file, (width, height))


def save(drawing):
    """
    Save a vector drawing to disk.

    :param drawing: Svgwrite drawing object.
    :return: None
    """
    drawing.save()


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
    new_vertices = transform[:-1]

    # Transpose the result to attain the same format as the original function argument, and return.
    return np.array(new_vertices.T)


def draw_straight_stroke(p0, p1, thk_factor, drawing):
    """
    Add a 2D straight stroke with rounded end-caps to the drawing.

    :param p0: Start point of the stroke, coincident with the arc center of the end-cap.
    :param p1: End point of the stroke, coincident with the arc center of the end-cap.
    :param thk_factor: Thickness scaling factor.
    :param drawing: Svgwrite drawing object.
    :return: None
    """

    # Define the basic outline properties.
    stroke_outline = drawing.path(stroke='black', stroke_width=0, fill='black')

    # Compute the Euclidean distance between points, yielding stroke length.
    length = point_utils.euclidean_dist(p0, p1)

    # Define stroke thickness for each point. TODO: May be better to take a linear transform approach (see snippet).
    t0 = point_utils.thickness_diffdir(p0, thk_factor)
    t1 = point_utils.thickness_diffdir(p1, thk_factor)

    # TODO: Apply translations before creating SVG paths.
    # Define a parameterised stroke outline, 2D straight stroke with rounded ends.
    stroke_outline.push('M', 0, 0)
    stroke_outline.push('L', length, 0)
    stroke_outline.push('A', t1 / 2, t1 / 2, 0, 1, 1, length, t1)
    stroke_outline.push('L', 0, t0)
    stroke_outline.push('A', t0 / 2, t0 / 2, 0, 1, 1, 0, 0)
    stroke_outline.push('Z')

    # Translate to p0.
    x_trans = p0.x
    y_trans = p0.y - t0 / 2
    stroke_outline.translate(x_trans, y_trans)

    # Rotate around p0 to achieve final position.
    angle = point_utils.heading(p0, p1)
    stroke_outline.rotate(angle, (0, t0 / 2))  # Center of rotation is relative to the original (0, 0).

    drawing.add(stroke_outline)
