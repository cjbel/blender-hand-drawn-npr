from blender_hand_drawn_npr import point_utils
import svgpathtools as svgp
import svgwrite
from collections import namedtuple
from rdp import rdp
from scipy import arange, spatial
import numpy as np

import blender_hand_drawn_npr.PathFitter as pf


def draw_all_the_things(points, origin_coords, outline_coords, markers, paths):
    drawing = svgwrite.Drawing("/tmp/bezier.svg", (110, 110))

    for point in points:
        circle = drawing.circle(center=(point.x, point.y), r=0.6, fill='red', stroke_width=0)
        drawing.add(circle)

    for marker in markers:
        circle = drawing.circle(center=(marker[0], marker[1]), r=0.6, fill='blue', stroke_width=0)
        drawing.add(circle)

    for coord in origin_coords:
        circle = drawing.circle(center=(coord[0], coord[1]), r=0.4, fill='green', stroke_width=0)
        drawing.add(circle)

    for coord in outline_coords:
        circle = drawing.circle(center=(coord[0], coord[1]), r=0.4, fill='orange', stroke_width=0)
        drawing.add(circle)

    for path in paths:
        p = drawing.path(stroke='black', stroke_width=0.2, fill='none')
        p.push(path.d())
        drawing.add(p)

    drawing.save()


def find_nearest_point(coord, points):
    """
    Find the nearest Point to the provided coordinate.

    :param coord:
    :param points:
    :return:
    """

    distance_map = {}

    for point in points:
        distance_map[point] = spatial.distance.euclidean((coord[0], coord[1]),
                                                         (point.x, point.y))

    return min(distance_map, key=distance_map.get)


# Define Points for testing.
Point = namedtuple("Point", "x y depth_intensity")
points = [Point(10, 10, 0.5),
          Point(15, 18, 0.5),
          Point(20, 20, 0.5),
          Point(30, 20, 0.5),
          Point(40, 15, 0.5),
          Point(80, 30, 0.5),
          Point(85, 50, 0.5),
          Point(90, 70, 0.5),
          Point(80, 100, 0.5)]
# points = [Point(10, 10, 0.5),
#           Point(15, 18, 0.5),
#           Point(20, 20, 0.5),
#           Point(30, 20, 0.5),
#           Point(40, 15, 0.5),
#           Point(60, 40, 0.5),
#           Point(80, 50, 0.5),
#           Point(90, 70, 0.5),
#           Point(100, 50, 0.5)]
# points = [Point(10, 10, 0.5),
#           Point(50, 10, 0.5)]
paths = []

# Extract coords.
point_coords = ([point.x, point.y] for point in points)
# Generate the SVG curve command which fits these Points.
inner_construction_svg_curve = pf.pathtosvg((pf.fitpath(point_coords, 3)))

# Bring into svgp.
inner_construction_curve = svgp.parse_path(inner_construction_svg_curve)
paths.append(inner_construction_curve)

# Minimum sampling interval.
interval = 4

# Temp for visualisation only.
origin_coords = []
outline_coords = []
markers = []

optimised_a = []
optimised_b = []

for path in paths:
    outline_coords_a = []
    outline_coords_b = []
    for n, segment in enumerate(path):

        # Note: svgpathtools defines segment parametrisation, t, over the domain 0 <= t <= 1.
        # First determine by how much t should be incremented between evaluation points.
        t_step = interval / segment.length()

        # Generate a list of parameter values. To avoid duplicate points between segments, ensure the endpoint of the
        # section (t = 1) is captured only if processing the final segment in the path.
        t = arange(0, 1, t_step)
        if n == len(path) - 1 and (1 not in t):
            t = np.append(t, 1)

        for step in t:
            normal = segment.normal(step)

            t_coord = [segment.point(step).real, segment.point(step).imag]
            origin_coords.append(t_coord)

            nearest_point = find_nearest_point(t_coord, points)  # TODO: This approach results in step changes in outline if thickness varies signficantly between Points. It would be better to assume a linear relationship between thickness values of neigbouring Points, so that the transition is more gradual.
            thickness = nearest_point.depth_intensity  # TODO: Probably should pass a thickness model in as an object.
            f = 1  # TODO: Stand-in for a thickness factor. See above.
            thickness *= f

            # a and b represent each side of the construction curve.
            outline_coord_a = segment.point(step) + (thickness * normal)
            outline_coord_b = segment.point(step) + (thickness * -normal)

            outline_coords_a.append([outline_coord_a.real, outline_coord_a.imag])
            outline_coords_b.append([outline_coord_b.real, outline_coord_b.imag])

    # Now, optimise and curve-fit the outline.
    optimised_a = rdp(outline_coords_a, .1)
    markers += optimised_a

    optimised_b = rdp(outline_coords_b, .1)
    # Reverse the order, so that the path follows clockwise around the overall outline.
    optimised_b.reverse()
    markers += optimised_b

    # Viz only.
    outline_coords += outline_coords_a
    outline_coords += outline_coords_b

a_svg_curve = pf.pathtosvg((pf.fitpath(optimised_a, 1)))
a_curve = svgp.parse_path(a_svg_curve)
paths.append(a_curve)

b_svg_curve = pf.pathtosvg((pf.fitpath(optimised_b, 1)))
b_curve = svgp.parse_path(b_svg_curve)
paths.append(b_curve)


# Viz only.
caps = []

print("a(0)", a_curve.point(0))
print("b(0)", b_curve.point(0))
print("inner(0)", inner_construction_curve.point(0))

print("a(1)", a_curve.point(1))
print("b(1)", b_curve.point(1))
print("inner(1)", inner_construction_curve.point(1))

draw_all_the_things(points, origin_coords, outline_coords, markers, paths)

drawing = svgwrite.Drawing("/tmp/bezier_complete.svg", (110, 110))

combined_path = paths[0].d() + " " + paths[1].d()
# print(combined_path)

p = drawing.path(stroke='black', stroke_width=0.2, fill='black')

# Top stroke.
p.push(paths[1].d())
print(paths[1].d())

# Start-cap.
p.push("A", 0.5, 0.5, 0, 1, 1, b_curve.point(0).real, b_curve.point(0).imag)

# Bottom stroke.
p.push(paths[2].d())
print(paths[2].d())

# p.push("M", a_curve.point(1).real, b_curve.point(1).imag)
# End-cap.
p.push("A", 0.5, 0.5, 0, 1, 1, a_curve.point(0).real, a_curve.point(0).imag)


print()

drawing.add(p)
drawing.save()
