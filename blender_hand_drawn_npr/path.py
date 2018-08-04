"""
A Path is an ordered collection of Points.
"""

from blender_hand_drawn_npr.point import Point
from scipy import spatial
from skimage.feature import corner_peaks, corner_harris, corner_subpix
from collections import deque
# from rdp import rdp
from skimage import measure
import numpy as np


class Path:

    def __init__(self, points=[]):
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

    # def simple_cull(self, n=5):
    #     """
    #     Discard all but the nth Points.
    #
    #     :return:
    #     """
    #
    #     remaining_points = []
    #     for i, point in enumerate(self.points):
    #         if i % n == 0:
    #             remaining_points.append(point)
    #
    #     self.points = remaining_points

    # def optimise(self):
    #     coords = [point.xy() for point in self.points]
    #     optimised_coords = rdp(coords, 1)
    #     self.points = [Point(coord[0], coord[1]) for coord in optimised_coords]

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


if __name__ == "__main__":

    a = [1, 2]
    path = Path(a)
    print(path.points)