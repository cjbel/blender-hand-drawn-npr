import logging

import svgwrite
from skimage import measure

from blender_hand_drawn_npr.primitives import Point, Path, Curve1D, Stroke

logger = logging.getLogger(__name__)


class Silhouette:
    """
    A Silhouette is a collection of Paths which capture the silhouette of the render subject.
    """

    def __init__(self, surface, colour):
        self.paths = []
        self.surface = surface
        self.colour = colour
        self.strokes = []

    def generate(self):
        """
        Make all such classes which produce paths implement this method to allow for polymorphic calls?
        :return: A collection of Paths which encompass the silhouette of the render subject.
        """

        logger.info("Finding Paths...")

        contours = measure.find_contours(self.surface.obj_image, 0.99)

        # Only a single contour is expected since the object image is well-defined.
        try:
            contours = contours[0]
        except IndexError:
            logger.warning("No Paths could be found!")
            return

        # Create the initial Path.
        path = Path([Point(coord[1], coord[0]) for coord in contours])

        # Initial Path must be split into multiple Paths if corners are present.
        if path.find_corners(self.surface.obj_image, 50, 13):
            self.paths += path.split_corners()
        else:
            self.paths.append(path)

        logger.info("Paths found: %d", len(self.paths))

        for path in self.paths:
            path.validate(self.surface)

            interval = 5
            optimisation_factor = 1
            fit_error = 0.1

            upper_curve = Curve1D(path=path,
                                  optimisation_factor=optimisation_factor, fit_error=fit_error)
            upper_curve.offset(interval=interval, surface=self.surface,
                               thickness_model=None)

            lower_curve = Curve1D(path=path,
                                  optimisation_factor=optimisation_factor, fit_error=fit_error)
            lower_curve.offset(interval=interval, surface=self.surface,
                               thickness_model=None, positive_direction=False)

            stroke = Stroke(upper_curve=upper_curve, lower_curve=lower_curve)

            svg_stroke = svgwrite.path.Path(fill=self.colour, stroke_width=0)
            svg_stroke.push(stroke.d)

            self.strokes.append(svg_stroke)

        logger.info("Strokes prepared: %d", len(self.strokes))


if __name__ == "__main__":
    pass
