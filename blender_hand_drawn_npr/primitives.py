import logging
import math
from collections import deque, namedtuple

import numpy as np
import svgpathtools as svgp
import svgwrite
from more_itertools import unique_everseen
from scipy import arange, spatial
from scipy.interpolate import interp1d
from skimage.feature import corner_harris, corner_peaks, corner_subpix
from skimage import measure

import blender_hand_drawn_npr.PathFitter as pf
from blender_hand_drawn_npr.models import Surface

logger = logging.getLogger(__name__)

Settings = namedtuple("Settings", ["cull_factor",
                                   "optimise_factor",
                                   "curve_fit_error",
                                   "harris_min_distance",
                                   "subpix_window_size",
                                   "curve_sampling_interval",
                                   "stroke_colour",
                                   "streamline_segments",
                                   "silhouette_thickness_parameters",
                                   "streamline_thickness_parameters",
                                   "uv_primary_trim_size",
                                   "uv_secondary_trim_size"])

ThicknessParameters = namedtuple("ThicknessParameters", ["const",
                                                         "z",
                                                         "diffdir",
                                                         "curvature"])


class Path:
    """
    A Path represents an immutable, ordered collection of image-space pixel coordinates ("points"), and the thickness
    values at each of these points.
    """

    def __init__(self, points, is_rc=False):

        # Points are represented internally as a tuple of (x, y) coordinates.
        if not is_rc:
            # Input coordinate are already given in terms of (x, y).
            self.__points = tuple(tuple(point) for point in points)
        else:
            # Input coordinates are given in terms of (row, column), so swap to (x, y).
            self.__points = tuple((point[1], point[0]) for point in points)

        self.__offset_vector = None
        self._curvatures = None

    @property
    def points(self):
        return self.__points

    @property
    def points_as_rc(self):
        return tuple(((point[1], point[0]) for point in self.__points))

    @property
    def offset_vector(self):
        return self.__offset_vector

    def round(self):
        """
        :return: New Path containing rounded points.
        """
        return Path(((int(round(point[0])), int(round(point[1]))) for point in self.__points))

    def nearest_neighbour(self, target_point):
        """
        :param target_point:
        :return: Point on the current Path which is nearest to the specified target_point in Euclidean space.
        """
        distance_map = {}

        for i, path_point in enumerate(self.__points):
            distance_map[i] = spatial.distance.euclidean(path_point, target_point)

        min_loc = min(distance_map, key=distance_map.get)

        return self.__points[min_loc]

    def find_corners(self, image, min_distance, window_size):
        """
        :param image:
        :param min_distance:
        :param window_size:
        :return: Points identified as corners.
        """

        # Locate corners, returned values are row/col coordinates (rcs).
        corner_rcs = corner_peaks(corner_harris(image), min_distance)
        subpix_rcs = corner_subpix(image=image, corners=corner_rcs, window_size=window_size)

        corners = []
        for i, subpix_rc in enumerate(subpix_rcs):
            if np.isnan(subpix_rc).any():
                # corners.append(tuple(corner_rcs[i].tolist()))
                corners.append((corner_rcs[i][1], corner_rcs[i][0]))
            else:
                # corners.append(tuple(subpix_rc.tolist()))
                corners.append((subpix_rc[1], subpix_rc[0]))

        return tuple(corners)

    def split_corners(self, corners):
        """
        :param corners:
        :return: New Path objects, each representing a distinct edge.
        """
        # Identify the index of each corner in this Path.
        corner_indices = []
        for corner in corners:
            corner = self.nearest_neighbour(corner)
            corner_indices.append(self.__points.index(corner))
        corner_indices.sort()

        # Rebase the list of points to ensure the first point in the list is a corner.
        rebase_value = corner_indices[0]
        rebased_indices = [x - rebase_value for x in corner_indices]
        rebased_points = deque(self.__points)
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

        return tuple(paths)

    def bump(self, surface):
        """
        In a meaningful path, all points lie on the surface such that the underlying surface attributes can be queried.
        If the Path has been generated based on find_contours, it is possible that inaccuracies can place the location
        slightly off the surface.

        :return: Path with points adjusted to valid surface locations in image-space.
        """

        points = list(self.__points)

        for i, point in enumerate(points):

            if surface.is_valid(point):
                continue

            else:
                # Need to find another pixel nearby which is valid. Due to the nature of find_contours, a pixel
                # with valid attributes will be found within 1 pixel of the original. So first, identify translations
                # required to shift pixel position by 1 pixel in each direction.
                step = 1
                pixel_translations = [[0, -step],  # N
                                      [0, step],  # S
                                      [step, 0],  # E
                                      [-step, 0],  # W
                                      [step, -step],  # NE
                                      [step, step],  # SE
                                      [-step, step],  # SW
                                      [-step, -step]]  # NW

                # Now evaluate the surface attributes of each neighbour.
                for j, pixel_translation in enumerate(pixel_translations):
                    candidate_point = (point[0] + pixel_translation[0],
                                       point[1] + pixel_translation[1])

                    try:
                        if surface.is_valid(candidate_point):
                            points[i] = candidate_point
                            # logger.debug("Invalid: %s replaced with: %s", point, candidate_point)
                            break
                        elif j == len(pixel_translations) - 1:
                            # Final loop iteration failed to find a match.
                            logger.warning("A valid point could not be found!")

                    except AssertionError:
                        logger.warning("Candidate point out of allowable range: %s", candidate_point)

        return Path(points)

    def remove_dupes(self):
        """
        :return: Path containing only unique points.
        """
        points = list(self.__points)
        unique = tuple(unique_everseen(points))

        return Path(unique)

    def simple_cull(self, n):
        """

        :param n: Minimum cull gap.
        :return: Path where only the nth points are preserved. The first and last points are always preserved.
        """

        points = list(self.__points)

        keep = []
        for i in range(0, len(points) - 1):
            if i % n == 0 and i < ((len(points) - 1) - (n - 1)):
                keep.append(points[i])
        keep.append(points[-1])

        return Path(keep)

    def optimise(self, n):
        points = measure.approximate_polygon(np.array(self.__points), n)

        return Path(points)

    def trim_uv(self, target_intensity, primary_image, secondary_image, primary_trim_size, secondary_trim_size):

        points = list(self.__points)

        min_allowable_primary = target_intensity - primary_trim_size
        max_allowable_primary = target_intensity + primary_trim_size

        min_allowable_secondary = secondary_image.min() + secondary_trim_size
        max_allowable_secondary = secondary_image.max() - secondary_trim_size

        last_was_accepted = None
        paths = []
        continuous_points = []
        for point in points:
            if min_allowable_primary <= primary_image[point[1], point[0]] <= max_allowable_primary and \
                    min_allowable_secondary <= secondary_image[point[1], point[0]] <= max_allowable_secondary:
                # Accept the point.
                continuous_points.append(point)
                last_was_accepted = True
            else:
                # Reject the point.
                if last_was_accepted:
                    # Create a Path from previously encountered continuous points.
                    paths.append(Path(continuous_points))
                    continuous_points.clear()
                    last_was_accepted = False

        # Create a Path from remaining points.
        if continuous_points:
            paths.append(Path(continuous_points))

        logger.debug("Paths after UV trim: %d", len(paths))

        return paths

    def compute_curvatures(self, primary_image, surface):

        # Compute first derivatives of planar magnitudes.
        first_derivatives = []
        for i in range(0, len(self.__points) - 1):
            cur_dim = primary_image[self.__points[i][1], self.__points[i][0]]
            cur_z = surface.at_point(self.__points[i][0], self.__points[i][1]).norm_z
            cur_magnitude = math.hypot(cur_dim, cur_z)

            next_dim = primary_image[self.__points[i + 1][1], self.__points[i + 1][0]]
            next_z = surface.at_point(self.__points[i + 1][0], self.__points[i + 1][1]).norm_z
            next_magnitude = math.hypot(next_dim, next_z)

            delta = abs(cur_magnitude - next_magnitude)
            first_derivatives.append(delta)

        first_derivatives = np.array(first_derivatives)
        nonzero_idx = np.nonzero(first_derivatives)
        nonzero_vals = first_derivatives[nonzero_idx]

        smoothed = []

        # For streamlines with zero curvature along their lengths there is no need to need to continue.
        if len(nonzero_idx[0]) == 0:
            self._curvatures = first_derivatives
            return

        # Pad start with zeros as needed.
        for i in range(0, nonzero_idx[0][0]):
            smoothed.append(0)

        # Interpolate between non-zero values.
        interp = interp1d(nonzero_idx[0], nonzero_vals)
        smoothed += [interp(x) for x in range(nonzero_idx[0][0], nonzero_idx[0][-1] + 1)]

        # Pad end with zeros as needed.
        for i in range(nonzero_idx[0][-1], len(first_derivatives)):
            smoothed.append(0)

        # from matplotlib import pyplot
        # pyplot.plot(first_derivatives)
        # pyplot.plot(smoothed)
        # pyplot.show()

        self._curvatures = smoothed

    # def compute_thicknesses(self, surface, thickness_parameters):
    # thicknesses = []
    # for i, point in enumerate(self.__points):
    #     constant_component = thickness_parameters.const
    #     surface_data = surface.at_point(point[0], point[1])
    #     z_component = (1 - surface_data.z) * thickness_parameters.z
    #     diffdir_component = (1 - surface_data.diffdir) * thickness_parameters.diffdir
    #     try:
    #         curvature_component = self._curvatures[i] * thickness_parameters.curvature
    #     except (IndexError, TypeError):
    #         curvature_component = 0
    #
    #     thickness = constant_component + z_component + diffdir_component + curvature_component
    #     thicknesses.append(thickness)
    #
    # self._thicknesses = tuple(thicknesses)

    def compute_offset_vector(self, surface, thickness_parameters):
        offsets = []
        for i, point in enumerate(self.points):
            constant_component = thickness_parameters.const
            surface_data = surface.at_point(point[0], point[1])
            z_component = (1 - surface_data.z) * thickness_parameters.z
            diffdir_component = (1 - surface_data.diffdir) * thickness_parameters.diffdir
            try:
                # curvature_component = self._curvatures[i] * thickness_parameters.curvature
                curvature_component = 0  # TODO: Fix.
            except (IndexError, TypeError):
                curvature_component = 0

            thickness = constant_component + z_component + diffdir_component + curvature_component
            offsets.append(thickness)

        offsets = tuple(offsets)
        logger.debug("Offset vector: %s", offsets)

        self.__offset_vector = tuple(offsets)


class Curve1D:
    """
    A Curve1D object represents a composite Bezier curve which approximates a Path.
    """

    def __init__(self, fit_path, settings):
        self.fit_path = fit_path
        self.fit_error = settings.curve_fit_error

        self.d = None
        self.d_c = None
        self.d_m = None

        self.__interval_points = []
        self.__offset_points = []

        self.__generate()

    def __generate(self):
        logger.debug("Starting path fit...")

        # if optimise:
        #     assert optimisation_factor is not None
        #     points = self.path.points
        #     keep = []
        #     for i in range(0, len(points) - 1):
        #         if i % optimisation_factor == 0:
        #             keep.append(points[i])
        #     keep.append(points[-1])
        #     self.cull_survivor_points = keep
        #     # points = measure.approximate_polygon(np.array(keep), 0.8)
        #     # self.optimised_path = Path(points.tolist())
        #     self.optimised_path = Path(points)
        #
        # else:
        #     points = np.array(path.points)

        self.d = pf.pathtosvg((pf.fitpath(self.fit_path.points, self.fit_error)))

        # Split the initial move-to from the remainder of the string.
        curve_start_index = self.d.index("C")
        self.d_m = self.d[0:curve_start_index - 1]
        self.d_c = self.d[curve_start_index:]
        logger.debug("Path fit complete...")

    # def __generate(self):
    #     self.__path_fit(path=self.path, fit_error=self.fit_error, optimise=True,
    #                     optimisation_factor=self.optimisation_factor)

    def offset(self, interval, hifi_path, offset_vector, positive_direction=True):

        self.__offset_points = []

        logger.debug("Starting offset...")
        for i, segment in enumerate(svgp.parse_path(self.d)):
            # Determine by how much the segment parametrisation, t, should be incremented between construction Points.
            # Note: svgpathtools defines t, over the domain 0 <= t <= 1.
            t_step = interval / segment.length()
            logger.debug("Segment length: %f", segment.length())
            logger.debug("T Step: %f", t_step)

            # Generate a list of parameter values. To avoid duplicate construction Points between segments, ensure the
            # endpoint of a segment (t = 1) is captured only if processing the final segment of the overall
            # construction curve.
            t = arange(0, 1, t_step)
            logger.debug("T list: %s", t)
            if i == len(svgp.parse_path(self.d)) - 1 and (1 not in t):
                t = np.append(t, 1)

            for step in t:
                logger.debug("Step: %f", step)
                # Extract the coordinates at this t-step.
                interval_point = [segment.point(step).real, segment.point(step).imag]
                self.__interval_points.append(interval_point)
                # Sometimes the point will be off the surface due to errors in curve fit. Perform nearest
                # neighbour to get valid surface attributes, but keep the point coordinates.
                # TODO: Shouldnt there be a validity check before calling this to avoid unnecessary calls?
                surface_point = hifi_path.nearest_neighbour(interval_point)
                surface_idx = hifi_path.points.index(surface_point)
                thickness = offset_vector[surface_idx]

                # Compute offset coordinates for each side (a and b) of the t-step.
                normal = segment.normal(step)

                if positive_direction:
                    dir = 1
                else:
                    dir = -1

                offset_coord = segment.point(step) + (thickness * normal * dir)
                offset_point = [offset_coord.real, offset_coord.imag]
                self.__offset_points.append(offset_point)

        if not positive_direction:
            offset_points = np.array(self.__offset_points)
            offset_points = np.flip(offset_points, 0)
            self.__offset_points = list(offset_points)

        logger.debug("Offset complete.")

        return Path(self.__offset_points)


class Stroke:
    def __init__(self, upper_curve, lower_curve):
        self.upper_curve = upper_curve
        self.lower_curve = lower_curve

        self.__generate()

    def __generate(self):
        logger.debug("Starting generate...")
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

        logger.debug("Generate complete.")


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
    path.bump(surface)

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
