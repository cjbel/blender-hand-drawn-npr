from blender_hand_drawn_npr.PathFitter import fitpath, pathtosvg
from collections import namedtuple
import svgwrite
from svgpathtools import parse_path, Line, Path, wsvg, paths2svg, path
from blender_hand_drawn_npr import point_utils
from rdp import rdp


def offset_curve(path, offset_distance, steps=1000):
    """Takes in a Path object, `path`, and a distance,
    `offset_distance`, and outputs an piecewise-linear approximation
    of the 'parallel' offset curve."""
    # Ref (verbatim): https://github.com/mathandy/svgpathtools#compatibility-notes-for-users-of-svgpath-v20
    nls = []
    for seg in path:
        for k in range(steps):
            t = k / float(steps)
            offset_vector = offset_distance * seg.normal(t)
            nl = Line(seg.point(t), seg.point(t) + offset_vector)
            nls.append(nl)
    connect_the_dots = [Line(nls[k].end, nls[k + 1].end) for k in range(len(nls) - 1)]
    if path.isclosed():
        connect_the_dots.append(Line(nls[-1].end, nls[0].end))
    offset_path = Path(*connect_the_dots)
    return offset_path

Point = namedtuple("Point", "x y depth_intensity")

points = [Point(10, 10, 0.5),
          Point(15, 18, 0.5),
          Point(20, 20, 0.5),
          Point(30, 20, 0.5),
          Point(40, 15, 0.5)]

coords = ([point.x, point.y] for point in points)

construction_curve = fitpath(coords, 2)
svg_construction_curve = pathtosvg(construction_curve)

# Resolution of stroke edges.
n = 100

# Generate the linear approximation of the offset curve.
upper_offset_curve = offset_curve(parse_path(svg_construction_curve), 2, n)
# lower_offset_curve = offset_curve(parse_path(svg_construction_curve), -2, n)

# Convert into x, y coords.
coords = [[segment.bpoints()[0].real, segment.bpoints()[1].imag] for segment in upper_offset_curve]

optimised_upper_curve = rdp(coords, 1)
construction_upper_curve = fitpath(optimised_upper_curve, 1)
svg_optimised_construction_curve = pathtosvg(construction_upper_curve)

# Draw all the things.
drawing = svgwrite.Drawing("/tmp/bezier.svg", (50, 50))

for point in points:
    circle = drawing.circle(center=(point[0], point[1]), r=1, fill='red', stroke_width=0)
    drawing.add(circle)

for coord in optimised_upper_curve:
    circle = drawing.circle(center=(coord[0], coord[1]), r=1, fill='blue', stroke_width=0)
    drawing.add(circle)

construction_curve_path = drawing.path(stroke='black', stroke_width=0.2, stroke_dasharray='0.5,0.5', fill='none')
construction_curve_path.push(svg_construction_curve)
drawing.add(construction_curve_path)

upper_offset_curve_path = drawing.path(stroke='yellow', stroke_width=0.5, fill='none')
upper_offset_curve_path.push(upper_offset_curve.d())
drawing.add(upper_offset_curve_path)

optimised_upper_curve_path = drawing.path(stroke='black', stroke_width=0.5, fill='none')
optimised_upper_curve_path.push(svg_optimised_construction_curve)
drawing.add(optimised_upper_curve_path)

# lower_offset_curve_path = drawing.path(stroke='yellow', stroke_width=0.5, fill='none')
# lower_offset_curve_path.push(lower_offset_curve.d())
# drawing.add(lower_offset_curve_path)

drawing.save()