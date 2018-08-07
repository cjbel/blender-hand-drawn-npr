import logging
from collections import deque

import numpy as np
import svgpathtools as svgp
import svgwrite
from scipy import arange, spatial
from skimage import measure
from skimage.feature import corner_harris, corner_peaks, corner_subpix

import blender_hand_drawn_npr.PathFitter as pf
from blender_hand_drawn_npr.models import Surface

logger = logging.getLogger(__name__)


class Path:

    def __init__(self, points):
        self.points = points
        self.corners = []

    def __round(self):
        self.points = [[int(round(point[0])), int(round(point[1]))] for point in self.points]

    def __is_valid(self, point, surface):
        surface_data = surface.at_point(point[0], point[1])
        is_valid = surface_data.obj != 0
        return is_valid

    def nearest_neighbour(self, target_point):

        # TODO: Needs tested, don't think this is working.

        distance_map = {}

        for i, path_point in enumerate(self.points):
            distance_map[i] = spatial.distance.euclidean(path_point, target_point)

        min_loc = min(distance_map, key=distance_map.get)

        return self.points[min_loc]

    def find_corners(self, image, min_distance, window_size):
        """
        Locate points which exist on the corners of the specified image.

        :param image:
        :param min_distance:
        :param window_size:
        :return:
        """

        # Locate corners, returned values are row/col coordinates (rcs).
        corner_rcs = corner_peaks(corner_harris(image), min_distance)

        if corner_rcs.any():
            # Locate a more accurate subpixel location of the corners.
            subpix_rcs = corner_subpix(image, corner_rcs, window_size)

            # Locate the nearest existing point closest to each subpixel location.
            for rc in subpix_rcs:
                corner = self.nearest_neighbour((rc[1], rc[0]))
                self.corners.append(corner)

        return self.corners

    def split_corners(self):
        # Split self into multiple new Path objects for each edge.

        # Identify the index of each corner in this Path.
        corner_indices = []
        for corner in self.corners:
            corner_indices.append(self.points.index(corner))
        corner_indices.sort()

        # Rebase the list of points to ensure the first point in the list is a corner.
        rebase_value = corner_indices[0]
        rebased_indices = [x - rebase_value for x in corner_indices]
        rebased_points = deque(self.points)
        rebased_points.rotate(-rebase_value)
        rebased_points = list(rebased_points)

        # Slice into new separate Path objects. Each Path is demarcated by a corner.
        paths = []
        for i in range(0, len(corner_indices)):
            if i != len(corner_indices) - 1:
                points = rebased_points[rebased_indices[i]:rebased_indices[i + 1] + 1]
                paths.append(Path(points))
            else:
                points = rebased_points[rebased_indices[i]:]
                paths.append(Path(points))

        return paths

    def validate(self, surface):
        """
        In a meaningful path, all points lie on the surface such that the underlying surface attributes can be queried.
        If the Path has been generated based on find_contours, it is possible that inaccuracies can place the location
        slightly off the surface.

        :return:
        """
        self.__round()

        for i, point in enumerate(self.points):

            if not self.__is_valid(point, surface):
                # Need to find another pixel nearby which passes the test. Due to the nature of rounding, a pixel with
                # valid attributes will be found within 1 pixel of the original. So first, identify translations
                # required to shift pixel position by 1 pixel in each direction.
                pixel_translations = [[1, 0],  # x+
                                      [0, 1],  # y+
                                      [-1, 0],  # x-
                                      [0, -1]]  # y-

                # Now evaluate the attributes of each neighbour.
                for pixel_translation in pixel_translations:
                    candidate_point = [point[0] + pixel_translation[0],
                                       point[1] + pixel_translation[1]]

                    try:
                        if self.__is_valid(candidate_point, surface):
                            logger.debug("Invalid: %s replaced with: %s", point, candidate_point)
                            self.points[i] = candidate_point
                            break

                    except AssertionError:
                        logger.debug("Candidate point out of allowable range: %s", candidate_point)

                logger.warning("A valid point could not be found!")


class Curve1D:
    def __init__(self, path, optimisation_factor, fit_error):
        self.path = path
        self.optimisation_factor = optimisation_factor
        self.fit_error = fit_error

        self.d = None
        self.d_c = None
        self.d_m = None

        self.interval_points = []
        self.offset_points = []

        self.__generate()

    def __path_fit(self, path, optimisation_factor, fit_error):
        path = measure.approximate_polygon(np.array(path.points), optimisation_factor)

        self.d = pf.pathtosvg((pf.fitpath(path, fit_error)))

        # Split the initial move-to from the remainder of the string.
        curve_start_index = self.d.index("C")
        self.d_m = self.d[0:curve_start_index - 1]
        self.d_c = self.d[curve_start_index:]

    def __generate(self):
        self.__path_fit(path=self.path, optimisation_factor=self.optimisation_factor, fit_error=self.fit_error)

    def offset(self, interval, surface, thickness_model, positive_direction=True):
        for i, segment in enumerate(svgp.parse_path(self.d)):
            # Determine by how much the segment parametrisation, t, should be incremented between construction Points.
            # Note: svgpathtools defines t, over the domain 0 <= t <= 1.
            t_step = interval / segment.length()

            # Generate a list of parameter values. To avoid duplicate construction Points between segments, ensure the
            # endpoint of a segment (t = 1) is captured only if processing the final segment of the overall
            # construction curve.
            t = arange(0, 1, t_step)
            if i == len(svgp.parse_path(self.d)) - 1 and (1 not in t):
                t = np.append(t, 1)

            for step in t:
                # Extract the coordinates at this t-step.
                interval_point = [segment.point(step).real, segment.point(step).imag]
                self.interval_points.append(interval_point)
                # Sometimes the point will be off the surface due to errors in curve fit. Perform nearest
                # neighbour to get valid surface attributes, but keep the point coordinates.
                # TODO: Shouldnt there be a validity check before calling this to avoid unnecessary calls?
                surface_point = self.path.nearest_neighbour(interval_point)
                surface_data = surface.at_point(surface_point[0], surface_point[1])

                # TODO: Think now about how to pass thickness requirements into here.
                # thickness = ((1 - surface_data.z) * 4) + 0.2
                thickness = 4

                # Compute offset coordinates for each side (a and b) of the t-step.
                normal = segment.normal(step)

                if positive_direction:
                    dir = 1
                else:
                    dir = -1

                offset_coord = segment.point(step) + (thickness * normal * dir)
                offset_point = [offset_coord.real, offset_coord.imag]
                self.offset_points.append(offset_point)

        if not positive_direction:
            offset_points = np.array(self.offset_points)
            offset_points = np.flip(offset_points, 0)
            self.offset_points = list(offset_points)

        self.__path_fit(path=Path(self.offset_points), optimisation_factor=self.optimisation_factor,
                        fit_error=self.fit_error)


class Stroke:
    def __init__(self, upper_curve, lower_curve):
        super().__init__()
        self.upper_curve = upper_curve
        self.lower_curve = lower_curve

        self.__generate()

    def __generate(self):
        upper_curve = svgp.parse_path(self.upper_curve.d)
        upper_curve_start = (upper_curve.start.real,
                             upper_curve.start.imag)
        upper_curve_end = (upper_curve.end.real,
                           upper_curve.end.imag)

        lower_curve = svgp.parse_path(self.lower_curve.d)
        lower_curve_start = (lower_curve.start.real,
                             lower_curve.start.imag)
        lower_curve_end = (lower_curve.end.real,
                           lower_curve.end.imag)

        r1 = spatial.distance.euclidean(upper_curve_end, lower_curve_start) / 2
        r2 = spatial.distance.euclidean(lower_curve_end, upper_curve_start) / 2

        p = svgwrite.path.Path()
        p.push(self.upper_curve.d)

        p.push("A",
               r1, r1,
               0,
               1, 1,
               lower_curve_start[0], lower_curve_start[1])

        p.push(self.lower_curve.d_c)

        p.push("A",
               r2, r2,
               0,
               1, 1,
               upper_curve_start[0], upper_curve_start[1])

        p.push("Z")

        # Call to either tostring or to_xml() is needed to create the dict 'd' attribute.
        p.tostring()
        self.d = p.attribs['d']


if __name__ == "__main__":

    # print(spatial.distance.euclidean([1, 0], [2, 0]))

    fake_image = np.ones((100, 100))
    # fake_image[1, 1] = 1
    surface = Surface(obj_image=fake_image,
                      z_image=fake_image,
                      diffdir_image=fake_image,
                      norm_image=fake_image,
                      u_image=fake_image,
                      v_image=fake_image)

    path = Path([[50, 20], [20, 50], [50, 80]])
    path.validate(surface)

    upper_curve = Curve1D(path=path, optimisation_factor=1, fit_error=0.1)
    upper_curve.offset(interval=2, surface=surface, thickness_model=None)

    lower_curve = Curve1D(path=path, optimisation_factor=1, fit_error=0.1)
    lower_curve.offset(interval=2, surface=surface, thickness_model=None, positive_direction=False)

    stroke = Stroke(lower_curve, upper_curve)

    drawing = svgwrite.Drawing("/tmp/out.svg", (100, 100))
    p = drawing.path(stroke_width=0, fill="black")
    p.push(stroke.d)
    drawing.add(p)
    drawing.save()
