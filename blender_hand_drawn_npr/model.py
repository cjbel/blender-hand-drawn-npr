"""
Preliminary domain model.

Ref: hertzmann2002, hertzmann2003
"""


class Image:
    def __init__(self, canvas):
        self.canvas = canvas
        self.strokes = []

    def add_stroke(self, stroke):
        self.strokes.append(stroke)


class Canvas:
    def __init__(self, x_res, y_res, colour='white'):
        self.x_res = x_res
        self.y_res = y_res
        self.colour = colour


class Stroke:
    def __init__(self, radius=1, colour='white'):
        self.radius = radius
        self.colour = colour
        self.control_points = []

    def add_control_point(self, r, c):
        self.control_points.append([r, c])

