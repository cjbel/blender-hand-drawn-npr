import svgwrite

import numpy as np
from skimage import io, draw, filters
import random


class Image:
    def __init__(self, canvas):
        self.canvas = canvas
        self.strokes = []

    def add_stroke(self, stroke):
        self.strokes.append(stroke)

    def remove_stroke(self, stroke):
        self.strokes.remove(stroke)


class Canvas:
    def __init__(self, x_res, y_res, colour='white'):
        self.x_res = x_res
        self.y_res = y_res
        self.colour = colour


class Stroke:
    def __init__(self, radius=1, control_points=[]):
        self.radius = radius
        self.control_points = control_points

    def add_control_point(self, r, c):
        self.control_points.append((r, c))


def rasterise_image(image):
    """ Convert an Image data structure into a raster image. """
    raster_image = np.zeros((image.canvas.y_res, image.canvas.x_res))

    for stroke in image.strokes:
        for n in range(0, len(stroke.control_points) - 1):
            # Pixel coords of a straight line between neighbouring control points.
            line_rr, line_cc = draw.line(stroke.control_points[n][0], stroke.control_points[n][1],
                                         stroke.control_points[n + 1][0], stroke.control_points[n + 1][1])
            for m in range(0, len(line_rr)):
                # Pixel coords of a solid circle equal to the stroke radius, centered on the pixel coord.
                circle_rr, circle_cc = draw.circle(line_rr[m], line_cc[m], stroke.radius)
                # Draw the circle.
                raster_image[circle_rr, circle_cc] = 1

    return raster_image


def vectorise_image(image):
    drawing = svgwrite.Drawing('out.svg', (image.canvas.x_res, image.canvas.y_res))

    for stroke in image.strokes:
        # Instantiate the Path object via drawing's "path" factory method.
        path = drawing.path(stroke='black', stroke_width=stroke.radius * 2, fill='none')
        # Starting point, no lines drawn here.

        for n, control_point in enumerate(stroke.control_points):
            if n == 0:
                path.push('M', control_point[1], control_point[0])
            else:
                path.push('L', control_point[1], control_point[0])

        # Add the path to the canvas.
        drawing.add(path)

    drawing.save()


def energy(candidate, reference, stroke_penalty=0, num_strokes=0):
    """ Ref Hertzmann2003 """
    e = 0
    for r, row in enumerate(candidate):
        for c, col in enumerate(row):
            image_intensity = col
            reference_intensity = reference[r, c]
            e += (image_intensity - reference_intensity) ** 2

    e += stroke_penalty * num_strokes

    return e


# Load the direct diffuse map.
infile = 'DiffDir0001.png'
diff_map = io.imread(infile, as_gray=True)

# Define a new image based on the same dimensions as above.
image = Image(Canvas(diff_map.shape[1], diff_map.shape[0]))

iterations = 5000

# Initial energy.
e = energy(rasterise_image(image), diff_map)

for n in range(0, iterations):
    # Define a candidate stroke to be centered around stroke_center, and arrange at 45 deg with fixed length.
    # TODO: rasterise_image will throw an exception when shapes are drawn outside the image boundary. Hacky fix for now is to ignore the image border (arbitary 20 pix).
    random_r = random.randint(20, image.canvas.y_res - 20)
    random_c = random.randint(20, image.canvas.x_res - 20)
    stroke_center = (random_r, random_c)
    offset = (-1, 1)
    candidate_stroke = Stroke(2, [np.subtract(stroke_center, offset), stroke_center, np.add(stroke_center, offset)])
    image.add_stroke(candidate_stroke)

    candidate_image = rasterise_image(image)
    candidate_image = filters.gaussian(candidate_image, 1)

    # Compute new energy.
    stroke_penalty = 5
    e_new = energy(candidate_image, diff_map, stroke_penalty, len(image.strokes))

    if e_new < e:
        e = e_new

    else:
        image.remove_stroke(candidate_stroke)

vectorise_image(image)

# Write to disk.
outfile = 'out.bmp'
io.imsave(outfile, rasterise_image(image))
