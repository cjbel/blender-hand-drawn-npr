"""
A Silhouette is a collection of Paths which capture the silhouette of the render subject.
"""

from blender_hand_drawn_npr.point import Point
from blender_hand_drawn_npr.path import Path

from skimage import measure, feature, io
import numpy as np


class Silhouette:

    def __init__(self, surface):
        self.paths = None
        self.surface = surface

    def generate(self):
        """
        Make all such classes which produce paths implement this method to allow for polymorphic calls?
        :return: A collection of Paths which encompass the silhouette of the render subject.
        """

        contours = measure.find_contours(self.surface.obj_image, 0.99)

        # Only a single contour is expected since the object image is well-defined.
        contours = contours[0]

        # Create the initial Path.
        path = Path([Point(coord[1], coord[0]) for coord in contours])

        # Initial Path must be split into multiple Paths if corners are present.
        paths = []
        if path.find_corners(self.surface.obj_image, 50, 13):
            paths += path.split_corners()
        else:
            paths.append(path)

        test_result = np.zeros_like(self.surface.obj_image)
        tone = 0.2
        for path in paths:
            # print(path.first_last_points())
            for point in path.points:
                test_result[point.rc()] = tone
            tone += 0.2

        io.imsave("/tmp/img.png", test_result)
