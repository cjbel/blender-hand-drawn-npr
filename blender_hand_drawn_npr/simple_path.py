"""
A simple script to demonstrate svgwrite paths.
"""

import svgwrite
import os

# Create the canvas.
img_file_root = 'blend_files/img/'
image_dim = (300, 300)
drawing = svgwrite.Drawing(os.path.join(img_file_root, 'simple_path.svg'), image_dim)

# Instantiate the Path object via drawing's "path" factory method.
path = drawing.path(stroke='black', stroke_width='2', fill='none')
# Starting point, no lines drawn here.
path.push('M', 100, 100)
# First line.
path.push('L', 200, 100)
# Second line.
path.push('L', 200, 200)
# Third line.
path.push('L', 100, 200)
# Close the shape, creating a fourth line leading back to the original point.
path.push('Z')

# Add the path to the canvas.
drawing.add(path)

drawing.save()
