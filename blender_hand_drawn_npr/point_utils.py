import math
from collections import namedtuple

import logging

logger = logging.getLogger(__name__)


def create_point(x, y, depth_intensity, diffdir_intensity):
    """
    Create a new Point data-object (as a named tuple).

    :return: Point.
    """
    Point = namedtuple("Point", "x y depth_intensity diffdir_intensity")
    return Point(x, y, depth_intensity, diffdir_intensity)


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
