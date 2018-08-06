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


class SVGPath:
    def __init__(self):
        self.d = None
        self.svg_obj = None
        self.svgpathtool_obj = None


class SVG1DCurve(SVGPath):
    def __init__(self):
        super().__init__()
        self.d_m = None
        self.d_c = None


class PathfittedCurve(SVG1DCurve):
    def __init__(self, path, fit_error):
        super().__init__()
        self.path = path
        self.fit_error = fit_error

        self.__generate()

    def __generate(self):
        coords = [point.xy() for point in self.path.points]
        self.d = pf.pathtosvg((pf.fitpath(coords, self.fit_error)))

        # Split the initial move-to from the remainder of the string.
        curve_start_index = self.d.index("C")
        self.d_m = self.d[0:curve_start_index - 1]
        self.d_c = self.d[curve_start_index:]

        self.svg_obj = svgwrite.path.Path(stroke="red", stroke_width=0.2, stroke_dasharray=(0.2, 0.2), fill="none")
        self.svg_obj.push(self.d)

        self.svgpathtool_obj = svgp.parse_path(self.d)


class OffsetCurve(SVG1DCurve):
    def __init__(self, path, fit_error, interval, surface, thickness_model, positive_direction=True):
        super().__init__()
        self.path = path
        self.fit_error = fit_error
        self.interval = interval
        self.surface = surface
        self.thickness_model = thickness_model
        self.positive_direction = positive_direction

        self.central_curve = None
        self.interval_points = []
        self.offset_points = []

        self.__generate()

    def __generate(self):
        self.central_curve = PathfittedCurve(self.path, self.fit_error)

        for i, segment in enumerate(self.central_curve.svgpathtool_obj):
            # Determine by how much the segment parametrisation, t, should be incremented between construction Points.
            # Note: svgpathtools defines t, over the domain 0 <= t <= 1.
            t_step = self.interval / segment.length()

            # Generate a list of parameter values. To avoid duplicate construction Points between segments, ensure the
            # endpoint of a segment (t = 1) is captured only if processing the final segment of the overall
            # construction curve.
            t = arange(0, 1, t_step)
            if i == len(self.central_curve.svgpathtool_obj) - 1 and (1 not in t):
                t = np.append(t, 1)

            for step in t:
                # Extract the coordinates at this t-step and create a Point.
                interval_point = Point(segment.point(step).real, segment.point(step).imag)
                self.interval_points.append(interval_point)
                # Sometimes the Point will be off the surface due to errors in curve fit. Perform nearest
                # neighbour to get valid surface attributes, but keep the Point coordinates.
                surface_point = self.path.nearest_neighbour(interval_point)
                surface_data = self.surface.at_point(surface_point.x, surface_point.y)

                # TODO: Think now about how to pass thickness requirements into here.
                thickness = ((1 - surface_data.z) * 4) + 0.2
                # thickness = 10

                # Compute offset coordinates for each side (a and b) of the t-step.
                normal = segment.normal(step)

                if self.positive_direction:
                    dir = 1
                else:
                    dir = -1

                offset_coord = segment.point(step) + (thickness * normal * dir)
                offset_point = Point(offset_coord.real, offset_coord.imag)
                self.offset_points.append(offset_point)

        # Optimise.
        offset_coords = np.array([point.xy() for point in self.offset_points])
        offset_coords = measure.approximate_polygon(offset_coords, 0.1)

        if not self.positive_direction:
            offset_coords = np.flip(offset_coords, 0)

        offset_points = [Point(coord[0], coord[1]) for coord in offset_coords]

        offset_curve = PathfittedCurve(path=Path(offset_points),
                                       fit_error=self.fit_error)

        self.d = offset_curve.d
        self.d_m = offset_curve.d_m
        self.d_c = offset_curve.d_c
        self.svg_obj = offset_curve.svg_obj
        self.svgpathtool_obj = offset_curve.svgpathtool_obj


class Stroke(SVGPath):
    def __init__(self, path, fit_error, interval, surface, thickness_model):
        super().__init__()
        self.path = path
        self.fit_error = fit_error
        self.interval = interval
        self.surface = surface
        self.thickness_model = thickness_model

        self.upper_curve = None
        self.lower_curve = None

        self.__generate()

    def __generate(self):
        self.upper_curve = OffsetCurve(path=self.path,
                                       fit_error=self.fit_error,
                                       interval=self.interval,
                                       surface=self.surface,
                                       thickness_model=self.thickness_model)
        self.lower_curve = OffsetCurve(path=self.path,
                                       fit_error=self.fit_error,
                                       interval=self.interval,
                                       surface=self.surface,
                                       thickness_model=self.thickness_model,
                                       positive_direction=False)

        upper_curve_start = (self.upper_curve.svgpathtool_obj.start.real,
                             self.upper_curve.svgpathtool_obj.start.imag)
        upper_curve_end = (self.upper_curve.svgpathtool_obj.end.real,
                           self.upper_curve.svgpathtool_obj.end.imag)

        lower_curve_start = (self.lower_curve.svgpathtool_obj.start.real,
                             self.lower_curve.svgpathtool_obj.start.imag)
        lower_curve_end = (self.lower_curve.svgpathtool_obj.end.real,
                           self.lower_curve.svgpathtool_obj.end.imag)

        r1 = spatial.distance.euclidean(upper_curve_end, lower_curve_start) / 2
        r2 = spatial.distance.euclidean(lower_curve_end, upper_curve_start) / 2

        self.svg_obj = svgwrite.path.Path(stroke="blue", stroke_width=0.2, stroke_dasharray=(0.2, 0.2), fill="none")

        self.svg_obj.push(self.upper_curve.d)

        self.svg_obj.push("A",
                          r1, r1,
                          0,
                          1, 1,
                          lower_curve_start[0], lower_curve_start[1])

        self.svg_obj.push(self.lower_curve.d_c)

        self.svg_obj.push("A",
                          r2, r2,
                          0,
                          1, 1,
                          upper_curve_start[0], upper_curve_start[1])

        self.svg_obj.push("Z")

        # Call to either tostring or to_xml() is needed to create the dict 'd' attribute.
        self.svg_obj.tostring()
        self.d = self.svg_obj.attribs['d']

        print(self.d)
        self.svgpathtool_obj = svgp.parse_path(self.d)


if __name__ == "__main__":
    surface = Surface(obj_image=np.zeros((100, 100)),
                      z_image=np.zeros((100, 100)),
                      diffdir_image=np.zeros((100, 100)),
                      norm_image=np.zeros((100, 100)),
                      u_image=np.zeros((100, 100)),
                      v_image=np.zeros((100, 100)))

    curve = Stroke(path=Path([Point(10, 20), Point(90, 20)]),
                   fit_error=0.5,
                   interval=1,
                   surface=surface,
                   thickness_model=None)

    drawing = svgwrite.Drawing("/tmp/out.svg", (100, 100))
    drawing.add(curve.svg_obj)
    drawing.add(curve.upper_curve.central_curve.svg_obj)
    drawing.save()
