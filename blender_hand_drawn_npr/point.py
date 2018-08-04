"""
A Point is a location in image x, y coordinate space.
"""

import numpy as np


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

    def surface_point(self, surface):
        """
        Transform the point into the nearest coordinate which lies on the surface.
        :return:
        """

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
            print("### INVALID POINT!!! ###")  # TODO: This will probably need to be implemented for the streamlines.


if __name__ == "__main__":
    point = Point(10, 20)
    print(point)
