"""
A stylistic representation of a Path.
"""
import logging

import numpy as np
import svgpathtools as svgp
import svgwrite
from scipy import arange
from skimage import measure

import blender_hand_drawn_npr.PathFitter as pf
from blender_hand_drawn_npr.point import Point

logger = logging.getLogger(__name__)


class Stroke:

    def __init__(self, path, surface):
        self.path = path
        self.surface = surface
        self.construction_curve = None
        self.offset_curve_a = None
        self.offset_curve_b = None
        self.svg_path = None

        self.__thicknesses = []
        self.__offset_coords_a = None
        self.__offset_coords_b = None

    def __build_construction_curve(self):
        coords = [point.xy() for point in self.path.points]

        # Produce a SVG curve (command) that fits the supplied coords.
        self.construction_curve = pf.pathtosvg((pf.fitpath(coords, 3)))

    def __build_offset_curves(self):
        # The overall construction curve will be divided into construction Points, which will be the origin from which
        # the offset curve coordinates are computed. Maintain separate lists for each side of the offset, a and b.
        offset_coords_a = []
        offset_coords_b = []

        construction_curve = svgp.parse_path(self.construction_curve)

        # Minimum inverval between construction Points.
        interval = 4

        for i, segment in enumerate(construction_curve):

            # Determine by how much the segment parametrisation, t, should be incremented between construction Points.
            # Note: svgpathtools defines t, over the domain 0 <= t <= 1.
            t_step = interval / segment.length()

            # Generate a list of parameter values. To avoid duplicate construction Points between segments, ensure the
            # endpoint of a segment (t = 1) is captured only if processing the final segment of the overall
            # construction curve.
            t = arange(0, 1, t_step)
            if i == len(construction_curve) - 1 and (1 not in t):
                t = np.append(t, 1)

            # Evaluate the construction points for this segment.
            for step in t:
                # Extract the coordinates at this t-step and create a construction Point.
                construction_point = Point(segment.point(step).real, segment.point(step).imag)
                # Sometimes the construction point will be off the surface due to errors in curve fit. Perform nearest
                # neighbour to get valid surface attributes, but keep the construction Point coordinates.
                surface_point = self.path.nearest_neighbour(construction_point)
                surface_data = self.surface.at_point(surface_point.x, surface_point.y)

                # TODO: Think now about how to pass thickness requirements into here.
                thickness = (1 - surface_data.z) * 10
                self.__thicknesses.append(thickness)

                # Compute offset coordinates for each side (a and b) of the t-step.
                normal = segment.normal(step)

                offset_coord_a = segment.point(step) + (thickness * normal)
                offset_coord_b = segment.point(step) + (thickness * -normal)

                offset_coords_a.append([offset_coord_a.real, offset_coord_a.imag])
                offset_coords_b.append([offset_coord_b.real, offset_coord_b.imag])

        # Optimise the offset coord paths.
        offset_coords_a = np.array(offset_coords_a)
        self.__offset_coords_a = measure.approximate_polygon(offset_coords_a, 0.1)

        offset_coords_b = np.array(offset_coords_b)
        offset_coords_b = measure.approximate_polygon(offset_coords_b, 0.1)
        # The end goal is to produce a single SVG path. Reverse the sequence of b to support this.
        self.__offset_coords_b = np.flip(offset_coords_b, 0)

        # Produce the SVG commands for each offset curve.
        self.offset_curve_a = pf.pathtosvg((pf.fitpath(self.__offset_coords_a, 3)))
        self.offset_curve_b = pf.pathtosvg((pf.fitpath(self.__offset_coords_b, 3)))

    def __build_svg_path(self):

        svg_path = svgwrite.path.Path(stroke_width=0, fill="black")

        # The stroke can be visualised as an offset curve (a), leading to an end-cap, leading to the other offset
        # curve (b), leading to the opposite end-cap. Construct the SVG command for this path.

        # Curve a.
        svg_path.push(self.offset_curve_a)

        # End-cap (arc)
        svg_path.push("A",
                      self.__thicknesses[-1], self.__thicknesses[-1],
                      0,
                      1, 1,
                      self.__offset_coords_b[0, 0], self.__offset_coords_b[0, 1])

        # Curve b.
        svg_path.push(self.offset_curve_b)

        # End-cap (arc).
        svg_path.push("A",
                      self.__thicknesses[0], self.__thicknesses[0],
                      0,
                      1, 1,
                      self.__offset_coords_a[0, 0], self.__offset_coords_a[0, 1])

        self.svg_path = svg_path

        logger.debug("SVG path: %s", self.svg_path.commands)

    def generate_svg_path(self):
        self.__build_construction_curve()
        self.__build_offset_curves()
        self.__build_svg_path()


if __name__ == "__main__":
    pass
