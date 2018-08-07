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


class Point:

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return str(self.xy())

    def xy(self):
        return self.x, self.y

    def rc(self):
        """
        :return: the coordinate value in format (row, column).
        """
        return int(self.y), int(self.x)

    def is_on_surface(self, surface):
        """
        Test whether the Point is located on the Surface by checking the value of the object map at this Point location.
        :param surface:
        :return:
        """

        surface_data = surface.at_point(self.x, self.y)
        return surface_data.obj != 0

    def validate(self, surface):
        self.x = int(round(self.x))
        self.y = int(round(self.y))

        if not self.is_on_surface(surface):
            logger.info("Invalid Point.")
            print("### INVALID POINT!!! ###")  # TODO: This will probably need to be implemented for the streamlines.


class Path:

    def __init__(self, points=None):
        if points is None:
            points = []
        self.points = points
        self.corners = []

    def add_point(self, point):
        """
        Add a single Point.
        """
        self.points.append(point)

    def add_points(self, points):
        """
        Add a list of Points.
        """
        self.points += points

    def start_end_points(self):
        """
        :return: Start and end Points of the Path.
        """

        return self.points[0], self.points[-1]

    def remove_duplicates(self):
        # TODO: Doesnt make sense if testing floats, very small hit rate.
        unique_points = []
        seen = set()
        for point in self.points:
            if (point.x, point.y) not in seen:
                seen.add((point.x, point.y))
                unique_points.append(point)

        self.points = unique_points

    def nearest_neighbour(self, point):
        distance_map = {}

        for path_point in self.points:
            distance_map[path_point] = spatial.distance.euclidean(path_point.xy(), point.xy())

        return min(distance_map, key=distance_map.get)

    def find_corners(self, image, min_distance, window_size):
        """
        Locate Points which exist on the corners of the specified image.

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

            # Locate the nearest existing Point closest to each subpixel location.
            for rc in subpix_rcs:
                subpix_corner = Point(rc[1], rc[0])
                corner = self.nearest_neighbour(subpix_corner)
                self.corners.append(corner)

        return self.corners

    def split_corners(self):
        # Split self into multiple new Path objects for each edge.

        # Identify the index of each corner in this Path.
        corner_indices = []
        for corner in self.corners:
            corner_indices.append(self.points.index(corner))
        corner_indices.sort()

        # Rebase the list of Points to ensure the first Point in the list is a corner.
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
        For a Path to be meaningful, all its Points should lie on the surface such that the underlying
        surface attributes can be queried. If the Path/Points has been generated based on find_contours, it is possible
        that inaccuracies can place the location slightly off the surface.

        :return:
        """
        [point.validate(surface) for point in self.points]

    def optimise(self):
        coords = [point.xy() for point in self.points]
        coords = np.array(coords)
        optimised_coords = measure.approximate_polygon(coords, 1)
        self.points = [Point(coord[0], coord[1]) for coord in optimised_coords]


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
        logger.debug("Path fitting...")

        coords = [point.xy() for point in path.points]

        coords = measure.approximate_polygon(np.array(coords), optimisation_factor)

        self.d = pf.pathtosvg((pf.fitpath(coords, fit_error)))
        logger.debug("D-string: %s", self.d)

        # Split the initial move-to from the remainder of the string.
        curve_start_index = self.d.index("C")
        self.d_m = self.d[0:curve_start_index - 1]
        self.d_c = self.d[curve_start_index:]

    def __generate(self):
        logger.debug("Generating curve from initial path...")
        self.__path_fit(path=self.path, optimisation_factor=self.optimisation_factor, fit_error=self.fit_error)

    def offset(self, interval, surface, thickness_model, positive_direction=True):
        logger.debug("Generating offset curve...")

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
                # Extract the coordinates at this t-step and create a Point.
                interval_point = Point(segment.point(step).real, segment.point(step).imag)
                self.interval_points.append(interval_point)
                # Sometimes the Point will be off the surface due to errors in curve fit. Perform nearest
                # neighbour to get valid surface attributes, but keep the Point coordinates.
                # TODO: Shouldnt there be a validity check before calling this to avoid unnecessary calls?
                surface_point = self.path.nearest_neighbour(interval_point)
                surface_data = surface.at_point(surface_point.x, surface_point.y)

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
                offset_point = Point(offset_coord.real, offset_coord.imag)
                self.offset_points.append(offset_point)

        offset_coords = np.array([point.xy() for point in self.offset_points])

        if not positive_direction:
            offset_coords = np.flip(offset_coords, 0)

        offset_points = [Point(coord[0], coord[1]) for coord in offset_coords]

        self.__path_fit(path=Path(offset_points), optimisation_factor=self.optimisation_factor,
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
    path = Path([Point(50, 20), Point(20, 50), Point(50, 80)])
    surface = Surface(obj_image=np.zeros((100, 100)),
                      z_image=np.zeros((100, 100)),
                      diffdir_image=np.zeros((100, 100)),
                      norm_image=np.zeros((100, 100)),
                      u_image=np.zeros((100, 100)),
                      v_image=np.zeros((100, 100)))

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
