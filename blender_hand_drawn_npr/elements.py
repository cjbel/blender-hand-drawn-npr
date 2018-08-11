import logging

import svgwrite
from skimage import measure

from blender_hand_drawn_npr.primitives import ThicknessParameters, Path, Curve1D, Stroke

logger = logging.getLogger(__name__)


def create_stroke(path, settings):
    logger.debug("Creating stroke with %d points...", len(path.points))

    upper_curve = Curve1D(path=path,
                          optimisation_factor=settings.rdp_epsilon, fit_error=settings.curve_fit_error)
    upper_curve.offset(interval=settings.curve_sampling_interval)

    lower_curve = Curve1D(path=path,
                          optimisation_factor=settings.rdp_epsilon, fit_error=settings.curve_fit_error)
    lower_curve.offset(interval=settings.curve_sampling_interval, positive_direction=False)

    return Stroke(upper_curve=upper_curve, lower_curve=lower_curve)


class Silhouette:
    """
    A Silhouette is a collection of Strokes which capture the silhouette of the render subject.
    """

    def __init__(self, surface, settings):
        self.surface = surface
        self.settings = settings
        self.paths = []
        self.svg_strokes = []

    def generate(self):
        """
        Make all such classes which produce paths implement this method to allow for polymorphic calls?
        :return: A collection of Paths which encompass the silhouette of the render subject.
        """

        contours = measure.find_contours(self.surface.obj_image, 0.99)

        # Only a single contour is expected since the object image is well-defined.
        try:
            contours = contours[0]
        except IndexError:
            logger.warning("No silhouette Paths could be found!")
            return

        # Create the initial Path.
        path = Path([[coord[1], coord[0]] for coord in contours])

        # Initial Path must be split into multiple Paths if corners are present.
        if path.find_corners(self.surface.obj_image, self.settings.harris_min_distance,
                             self.settings.subpix_window_size):
            self.paths += path.split_corners()
        else:
            self.paths.append(path)

        logger.info("Silhouette Paths found: %d", len(self.paths))

        for path in self.paths:
            path.bump(self.surface)

            # TODO: Have an entry for this in settings.
            thickness_parameters = ThicknessParameters(const=0.25, z=2, diffdir=0, curvature=0)
            path.compute_thicknesses(self.surface, thickness_parameters)

            stroke = create_stroke(path=path, settings=self.settings)
            svg_stroke = svgwrite.path.Path(fill=self.settings.stroke_colour, stroke_width=0)
            svg_stroke.push(stroke.d)
            self.svg_strokes.append(svg_stroke)

            # #####################################################################################
            # # TODO: THIS BLOCK IS FOR TESTING, PLOTS THE CONSTRUCTION CURVE.
            # construction_curve = Curve1D(path=path,
            #                              optimisation_factor=self.settings.rdp_epsilon,
            #                              fit_error=self.settings.curve_fit_error)
            # center_stroke = svgwrite.path.Path(stroke="blue", stroke_width=0.25, fill="none")
            # center_stroke.push(construction_curve.d)
            # self.svg_strokes.append(center_stroke)
            #
            # points = construction_curve.path.points
            # for point in points:
            #     self.svg_strokes.append(svgwrite.shapes.Circle((point[0], point[1]), r=0.1))
            #
            # points = construction_curve.optimised_path.points
            # for point in points:
            #     self.svg_strokes.append(svgwrite.shapes.Circle((point[0], point[1]), r=0.3, fill="pink"))
            #
            # # points = stroke.upper_curve.interval_points
            # # for point in points:
            # #     self.svg_strokes.append(svgwrite.shapes.Circle((point[0], point[1]), r=0.3, fill="yellow"))
            #
            # points = stroke.upper_curve.offset_points
            # for point in points:
            #     self.svg_strokes.append(svgwrite.shapes.Circle((point[0], point[1]), r=0.3, fill="green"))
            #
            # points = stroke.upper_curve.optimised_path.points
            # for point in points:
            #     self.svg_strokes.append(svgwrite.shapes.Circle((point[0], point[1]), r=0.3, fill="magenta"))
            #
            # outline_stroke = svgwrite.path.Path(stroke="red", stroke_width=0.25, fill="none")
            # outline_stroke.push(stroke.lower_curve.d)
            # outline_stroke.push(stroke.upper_curve.d)
            # self.svg_strokes.append(outline_stroke)
            # #####################################################################################

        logger.info("Silhouette Strokes prepared: %d", len(self.svg_strokes))


class Streamlines:
    """
    Streamlines are a collection of SVG Streamline strokes.
    """

    def __init__(self, surface, settings):
        self.settings = settings
        self.surface = surface
        self.svg_strokes = []

    def generate(self):
        u_image = self.surface.u_image
        v_image = self.surface.v_image
        n = self.settings.streamline_segments

        u_separation, v_separation = (u_image.max() - u_image.min()) / n, \
                                     (v_image.max() - v_image.min()) / n
        logger.debug("Streamline separation (u, v): %s, %s", u_separation, v_separation)

        u_intensities = []
        for streamline_pos in range(1, n):
            u_intensities.append(streamline_pos * u_separation)
        logger.debug("Intensities (u): %s", u_intensities)

        v_intensities = []
        for streamline_pos in range(1, n):
            v_intensities.append(streamline_pos * v_separation)
        logger.debug("Intensities (v): %s", v_intensities)

        strokes = []
        for intensity in u_intensities:
            norm_image_component = self.surface.norm_x
            logger.debug("Creating (u) streamline at intensity %d...", intensity)
            u_streamline = Streamline(uv_image_component=u_image,
                                      norm_image_component=norm_image_component,
                                      surface=self.surface,
                                      intensity=intensity,
                                      settings=self.settings)
            u_streamline.generate()
            strokes += u_streamline.strokes

        for intensity in v_intensities:
            norm_image_component = self.surface.norm_y
            logger.debug("Creating (v) streamline at intensity %d...", intensity)
            v_streamline = Streamline(uv_image_component=v_image,
                                      norm_image_component=norm_image_component,
                                      surface=self.surface,
                                      intensity=intensity,
                                      settings=self.settings)
            v_streamline.generate()
            strokes += v_streamline.strokes

        for stroke in strokes:
            svg_stroke = svgwrite.path.Path(fill=self.settings.stroke_colour, stroke_width=0)
            svg_stroke.push(stroke.d)
            self.svg_strokes.append(svg_stroke)

            # #####################################################################################
            # # TODO: THIS BLOCK IS FOR TESTING, PLOTS THE CONSTRUCTION CURVE.
            # construction_curve = Curve1D(path=stroke.upper_curve.path,
            #                              optimisation_factor=self.settings.rdp_epsilon,
            #                              fit_error=self.settings.curve_fit_error)
            # center_stroke = svgwrite.path.Path(stroke="blue", stroke_width=0.25, fill="none")
            # center_stroke.push(construction_curve.d)
            # self.svg_strokes.append(center_stroke)
            #
            # points = stroke.upper_curve.path.points
            # for point in points:
            #     self.svg_strokes.append(svgwrite.shapes.Circle((point[0], point[1]), r=0.3, fill="red"))
            #
            # points = stroke.upper_curve.optimised_path.points
            # for point in points:
            #     self.svg_strokes.append(svgwrite.shapes.Circle((point[0], point[1]), r=0.3, fill="red"))
            #
            # #####################################################################################

        logger.info("Streamline Strokes prepared: %d", len(self.svg_strokes))


class Streamline:
    """
    A Streamline is a collection of Strokes which follow a specified UV intensity value.
    """

    def __init__(self, uv_image_component, norm_image_component, surface, intensity, settings):
        self.uv_image_component = uv_image_component
        self.norm_image_component = norm_image_component
        self.surface = surface
        self.intensity = intensity
        self.settings = settings
        self.paths = []
        self.strokes = []

    def generate(self):
        contours = measure.find_contours(self.uv_image_component, self.intensity)
        logger.debug("Streamline contours found: %d", len(contours))

        for contour in contours:
            # Sometimes a contour of small length (~5-10 is found, consider a check here to reject them.
            if len(contour) < 10:
                logger.debug("Contour of length %s rejected.", len(contour))
                break
            logger.debug("Contour length: %d", len(contour))

            # Create the Path.
            path = Path([[coord[1], coord[0]] for coord in contour])
            path.bump(self.surface)
            path.trim_uv(self.intensity, self.uv_image_component)

            # TODO: Not sure if this is really needed, but it is possible the path will be trimmed to zero length (may only be an issue with spheres?).
            if len(path.points) == 0:
                logger.debug("Zero length path after trim.")
                break

            path.compute_curvatures(self.norm_image_component, self.surface)

            # TODO: Have an entry for this in settings.
            # thickness_parameters = ThicknessParameters(const=0.1, z=0, diffdir=0, curvature=0.0002)
            thickness_parameters = ThicknessParameters(const=0.1, z=1, diffdir=0, curvature=0)
            path.compute_thicknesses(self.surface, thickness_parameters)

            stroke = create_stroke(path=path, settings=self.settings)
            self.strokes.append(stroke)

        # import numpy as np
        # import matplotlib.pyplot as plt
        # conts = [np.array(path.points)]
        # # Display the image and plot all contours found
        # fig, ax = plt.subplots()
        # ax.imshow(self.primary_image, interpolation='nearest', cmap=plt.cm.gray)
        #
        # for cont in conts:
        #     ax.plot(cont[:, 1], cont[:, 0], linewidth=2)
        # plt.show()


if __name__ == "__main__":
    pass
