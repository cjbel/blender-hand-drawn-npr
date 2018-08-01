import math
from collections import namedtuple
import rdp
import numpy as np

import logging

logger = logging.getLogger(__name__)


def create_point(x, y, render_pass):
    """
    Create a new Point data-object (as a named tuple).

    Notes:
        - Floating point inputs for x, y will be changed to ints, to match pixel-space.
        - Only valid points will be returned, i.e. points which exist within the Subject boundary.

    :return: A valid Point, or None if a valid Point cannot be found.
    """
    # Convert approximate pixel location (float) into concrete pixel location (int).
    x, y = np.round(x).astype(np.int), np.round(y).astype(np.int)

    Point = namedtuple("Point", "x y depth_intensity diffdir_intensity u v")

    point = Point(x=x,
                  y=y,
                  depth_intensity=render_pass.depth[y, x],
                  diffdir_intensity=render_pass.diffdir[y, x],
                  u=render_pass.uv[:, :, 0][y, x],
                  v=render_pass.uv[:, :, 1][y, x])

    # Rounding as above may shift the pixel position beyond the Subject boundary. This will cause incorrect attributes
    # to be read from the images (depth, diffdir etc). If the function below evaluates to False, this is a strong
    # indicator of this mismatch.
    # TODO: This may cause false positives, since 0, 0 uv will be valid at one Point. Consider using object map instead?
    def is_valid(query_point):
        return any([query_point.diffdir_intensity != 0,
                    query_point.u != 0,
                    query_point.v != 0])

    if is_valid(point):
        logger.debug("Valid: %s ", point)
        return point

    else:
        # Need to find another pixel nearby which passes the test. Due to the nature of rounding, a pixel with valid
        # attributes will be found within 1 pixel of the original. So first, identify translations required to shift
        # pixel position by 1 pixel in each direction.
        pixel_translations = [[1, 0],  # x+
                              [0, 1],  # y+
                              [-1, 0],  # x-
                              [0, -1]]  # y-

        # Now evaluate the attributes of each neighbour.
        for pixel_translation in pixel_translations:
            candidate_x = x + pixel_translation[0]
            candidate_y = y + pixel_translation[1]

            try:
                candidate_point = Point(x=candidate_x,
                                        y=candidate_y,
                                        depth_intensity=render_pass.depth[candidate_y, candidate_x],
                                        diffdir_intensity=render_pass.diffdir[candidate_y, candidate_x],
                                        u=render_pass.uv[:, :, 0][candidate_y, candidate_x],
                                        v=render_pass.uv[:, :, 1][candidate_y, candidate_x])
            except IndexError:
                logger.debug("Candidate Point index out of bounds: %s, %s", candidate_x, candidate_y)
                break

            if is_valid(candidate_point):
                logger.debug("Invalid: %s replaced with: %s", point, candidate_point)
                return candidate_point

        logger.warning("A valid Point could not be found.")
        return None


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


def coords_to_points(coords, render_pass):
    """
    Convenience function to convert a list of coordinate values into a list of Points.

    :param coords:
    :param render_pass:
    :return:
    """
    points = []
    for coord in coords:
        point = create_point(x=coord[1],
                             y=coord[0],
                             render_pass=render_pass)
        if point is not None:
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
