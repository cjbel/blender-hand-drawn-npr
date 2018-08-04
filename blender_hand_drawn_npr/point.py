"""
A Point is a location in image x, y coordinate space.
"""

import numpy as np


class Point:

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def xy(self):
        return self.x, self.y

    def rc(self):
        """
        :return: the coordinate value in format (row, column).
        """
        return int(self.y), int(self.x)

    def surface_point(self, surface):
        """
        Transform the point into the nearest coordinate which lies on the surface.
        :return:
        """

    def is_on_surface(self, surface):
        """
        Test whether the Point is located on the Surface.
        :param surface:
        :return:
        """


if __name__ == "__main__":
    point = Point(10, 20)
    print(point)
