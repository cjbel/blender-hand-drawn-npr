import logging

from skimage import measure

from blender_hand_drawn_npr.primitives import Point, Path, Stroke

logger = logging.getLogger(__name__)


class Silhouette:
    """
    A Silhouette is a collection of Paths which capture the silhouette of the render subject.
    """

    def __init__(self, surface):
        self.paths = []
        self.surface = surface
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
            path.optimise()
            stroke = Stroke(path=path,
                            fit_error=0.1,
                            interval=5,
                            surface=self.surface,
                            thickness_model=None)
            self.strokes.append(stroke)

        logger.info("Strokes prepared: %d", len(self.strokes))


if __name__ == "__main__":
    pass
