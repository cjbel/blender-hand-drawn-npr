from blender_hand_drawn_npr import PathFitter
from skimage import io, draw
import numpy as np
import svgwrite

drawing = svgwrite.Drawing("/tmp/bezier.svg", (200, 200))

points = ((10, 10), (10, 20), (20, 20), (20, 10), (10, 10))
# points = ((10, 10), (22, 20), (30, 30), (40, 40), (70, 60), (100, 40))
# points = ((10, 10), (25, 20), (30, 30), (40, 40), (50, 80))
for point in points:
    circle = drawing.circle(center=(point[0], point[1]), r=2, stroke='red', stroke_width=1)
    drawing.add(circle)

fitted_curves = PathFitter.fitpath(points, 1)
svg_commands = PathFitter.pathtosvg(fitted_curves)

curve_path = drawing.path(stroke='black', stroke_width='2', fill='none')
curve_path.push(svg_commands)

# Add the path to the canvas.
drawing.add(curve_path)

drawing.save()

