"""
A stylistic representation of a Path.
"""

from blender_hand_drawn_npr.point import Point
import blender_hand_drawn_npr.PathFitter as pf
import svgpathtools as svgp
from scipy import arange, spatial
import numpy as np
from skimage import measure


class Stroke:

    def __init__(self, path, layer, surface):
        self.path = path
        self.layer = layer
        self.surface = surface
        self.construction_curve = None
        self.offset_curve_a = None
        self.offset_curve_b = None
        self.command = None

    def __build_construction_curve(self):
        coords = [point.xy() for point in self.path.points]

        # Produce a SVG curve (command) that fits the supplied coords.
        self.construction_curve = pf.pathtosvg((pf.fitpath(coords, 3)))

    def __build_offset_curves(self):
        # The overall construction curve will be divided into construction Points, which will be the origin from which
        # the offset curve coordinates are computed. Maintain separate lists for each side of the offset, a and b.
        offset_coords_a = []
        offset_coords_b = []

        # Bring the construction curve into svgp for processing.
        construction_curve = svgp.parse_path(self.construction_curve)

        # Minimum inverval between construction Points.
        interval = 4

        for i, segment in enumerate(construction_curve):

            # Determine by how much the segment parametrisation, t, should be incremented between construction Points.
            # Note: svgpathtools defines t, over the domain 0 <= t <= 1.
            t_step = interval / segment.length()

            # Generate a list of parameter values. To avoid duplicate construction Points between segments, ensure the
            # endpoint of the section (t = 1) is captured only if processing the final segment of the overall
            # construction curve.
            t = arange(0, 1, t_step)
            if i == len(construction_curve) - 1 and (1 not in t):
                t = np.append(t, 1)

            # Evaluate the construction points for this segment.
            for step in t:

                # Extract the coordinates at this t-step and create a construction Point.
                construction_point = Point(segment.point(step).real, segment.point(step).imag)
                # Sometimes the construction point will be off the surface due to errors in curve fit. Perform a nearest
                # neighbour to get valid surface attributes, but keep the construction Point coordinates.
                surface_point = self.path.nearest_neighbour(construction_point)
                surface_data = self.surface.at_point(surface_point.x, surface_point.y)

                # TODO: Think now about how to pass thickness requirements into here.
                thickness = surface_data.z * 5

                # Compute offset coordinates for each side (a and b) of the t-step.
                normal = segment.normal(step)

                offset_coord_a = segment.point(step) + (thickness * normal)
                offset_coord_b = segment.point(step) + (thickness * -normal)

                offset_coords_a.append([offset_coord_a.real, offset_coord_a.imag])
                offset_coords_b.append([offset_coord_b.real, offset_coord_b.imag])

        # Optimise the offset coord paths.
        offset_coords_a = np.array(offset_coords_a)
        offset_coords_a = measure.approximate_polygon(offset_coords_a, 1)
        offset_coords_b = np.array(offset_coords_b)
        offset_coords_b = measure.approximate_polygon(offset_coords_b, 1)

        # Produce SVG curves (commands) that fit the supplied coords.
        self.offset_curve_a = pf.pathtosvg((pf.fitpath(offset_coords_a, 1)))
        self.offset_curve_b = pf.pathtosvg((pf.fitpath(offset_coords_b, 1)))

    def generate_svg(self):
        self.__build_construction_curve()
        self.__build_offset_curves()
        # Temp for testing.
        self.command = self.offset_curve_a
