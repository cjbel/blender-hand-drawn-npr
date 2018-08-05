"""
Streamlines is a collection of Paths which capture the (u or v) directional streamlines of the render subject.
"""


class Streamlines:

    def __init__(self, surface, n):
        self.paths = None
        self.surface = surface
        self.n = n

    def generate(self):
        """
        Make all such classes which produce paths implement this method to allow for polymorphic calls?
        :return: A collection of Paths which capture the (u or v) directional streamlines of the render subject.
        """

