import math
from collections import namedtuple
import rdp

import logging

logger = logging.getLogger(__name__)


def create_point(x, y, depth_intensity, diffdir_intensity, ux, uy):
    """
    Create a new Point data-object (as a named tuple).

    :return: Point.
    """
    Point = namedtuple("Point", "x y depth_intensity diffdir_intensity ux uy")
    return Point(x, y, depth_intensity, diffdir_intensity, ux, uy)


def horizontal_delta(p0, p1):
    """ Compute the horizontal delta between two Points.

    :param p0: Start point.
    :param p1: End point.
    :return: Horizontal delta.
    """
    h_delta = p1.x - p0.x
    logger.debug("Horizontal delta between %f and %f: %f", p0.x, p1.x, h_delta)

    return h_delta


def vertical_delta(p0, p1):
    """ Compute the vertical delta between two Points.

    :param p0: Start point.
    :param p1: End point.
    :return: Vertical delta.
    """
    v_delta = p1.y - p0.y
    logger.debug("Vertical delta between %f and %f: %f", p0.y, p1.y, v_delta)
    return v_delta


def euclidean_dist(p0, p1):
    """ Compute the Euclidean distance between two Points.

    :param p0: Start point.
    :param p1: End point.
    :return: Euclidean distance.
    """
    e_dist = math.hypot(horizontal_delta(p0, p1), vertical_delta(p0, p1))
    logger.debug("Euclidean distance between %s and %s: %f", p0, p1, e_dist)
    return e_dist


def heading(p0, p1):
    """ Compute the heading between two Points.

    :param p0: Start point.
    :param p1: End point.
    :return: Heading in degrees, from horizontal (x+)
    """
    return math.degrees(math.atan2(vertical_delta(p0, p1), horizontal_delta(p0, p1)))


def thickness_depth(p, factor):
    """ Compute the stroke thickness at the specified Point based on the z-depth at that Point.

    :param p: Point.
    :param factor: Scale factor.
    :return: Thickness.
    """
    thickness = (1 - p.depth_intensity) * factor
    logger.debug("Thickness at %s, with factor %f: %f", p, factor, thickness)

    return thickness


def thickness_diffdir(p, factor):
    """ Compute the stroke thickness at the specified Point based on the diffuse direct intensity at that Point.

    :param p: Point.
    :param factor: Scale factor.
    :return: Thickness.
    """
    thickness = (1 - p.diffdir_intensity) * factor
    logger.debug("Thickness at %s, with factor %f: %f", p, factor, thickness)

    return thickness


def coords_to_points(coords, depth_image, diffdir_image, u_image, v_image):
    """
    Convenience function to convert a list of coordinate values into a list of Points.

    :param coords:
    :param depth_image:
    :param diffdir_image:
    :param u_image:
    :param v_image:
    :return:
    """
    points = []
    for coord in coords:
        r, c = coord[0], coord[1]
        depth_intensity = depth_image[r, c]
        diffdir_intensity = diffdir_image[r, c]
        ux = u_image[r, c]
        uy = v_image[r, c]

        point = create_point(x=c,
                             y=r,
                             depth_intensity=depth_intensity,
                             diffdir_intensity=diffdir_intensity,
                             ux=ux,
                             uy=uy)
        points.append(point)

    return points


def remove_duplicate_coords(points):
    """
    Remove Points with duplicate coordinates in a list of Points, preserving the original order.

    :param points:
    :return:
    """
    unique_points = []
    seen = set()
    for point in points:
        if (point.x, point.y) not in seen:
            seen.add((point.x, point.y))
            unique_points.append(point)

    return unique_points


def linear_optimise(points):
    """
    Simplify a list of coordinates whilst maintaining the overall shape of the path they represent.

    :param points: list of Points.
    :return: Optimised list of Points.
    """
    logger.debug("Unoptimised vertex count: %d", len(points))

    # Extract all coords from Points.
    coords = [[point.x, point.y] for point in points]

    # Optimise.
    optimised_coords = rdp.rdp(coords, epsilon=1)

    # Relate coords back to Points.
    optimised_points = []
    for optimised_coord in optimised_coords:
        for point in points:
            if optimised_coord == [point.x, point.y]:
                optimised_points.append(point)

    logger.debug("Optimised vertex count: %d", len(optimised_points))

    return optimised_points
