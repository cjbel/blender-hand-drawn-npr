import logging

import svgwrite
from skimage import measure

from blender_hand_drawn_npr.primitives import Path, Curve1D, Stroke

logger = logging.getLogger(__name__)


def create_stroke(fit_path, hifi_path, thickness_parameters, surface, settings):
    logger.debug("Creating stroke with %d points...", len(fit_path.points))

    construction_curve = Curve1D(fit_path=fit_path, settings=settings)

    upper_path = construction_curve.offset(interval=settings.curve_sampling_interval,
                                           hifi_path=hifi_path,
                                           thickness_parameters=thickness_parameters,
                                           surface=surface,
                                           positive_direction=True)

    upper_curve = Curve1D(fit_path=upper_path, settings=settings)

    lower_path = construction_curve.offset(interval=settings.curve_sampling_interval,
                                           hifi_path=hifi_path,
                                           thickness_parameters=thickness_parameters,
                                           surface=surface,
                                           positive_direction=False)
    lower_curve = Curve1D(fit_path=lower_path, settings=settings)

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

        # find_contours may return more than one contour set. The "correct" contour is generally the longest path in
        # the set.
        contour = max(contours, key=len)

        # Create the initial Path.
        path = Path([[coord[1], coord[0]] for coord in contour])

        # Initial Path must be split into multiple Paths if corners are present.
        corners = path.find_corners(self.surface.obj_image, self.settings.harris_min_distance,
                                    self.settings.subpix_window_size)
        logger.info("Silhouette corners found: %d", len(corners))

        if corners:
            self.paths += path.split_corners(corners)
        else:
            self.paths.append(path)

        logger.info("Silhouette Paths found: %d", len(self.paths))

        for path in self.paths:
            hifi_path = path.round().bump(self.surface).remove_dupes().simple_cull(self.settings.cull_factor)
            fit_path = hifi_path.optimise(self.settings.optimise_factor)

            if len(path.points) < 2:
                logger.debug("Silhouette path of length %d ignored.", len(path.points))
                continue

            logger.debug("Creating Silhouette stroke...")
            stroke = create_stroke(fit_path=fit_path,
                                   hifi_path=hifi_path,
                                   thickness_parameters=self.settings.silhouette_thickness_parameters,
                                   surface=self.surface,
                                   settings=self.settings)
            svg_stroke = svgwrite.path.Path(fill=self.settings.stroke_colour, stroke_width=0)
            svg_stroke.push(stroke.d)
            self.svg_strokes.append(svg_stroke)

            # #####################################################################################
            # # TODO: THIS BLOCK IS FOR TESTING.
            #
            # curve = Curve1D(path=path, fit_error=self.settings.curve_fit_error)
            # svg_stroke = svgwrite.path.Path(stroke="black", fill="none", stroke_width=0.2)
            # svg_stroke.push(curve.d)
            # self.svg_strokes.append(svg_stroke)
            #
            # offset_path_upper = curve.offset(interval=self.settings.curve_sampling_interval,
            #                                  surface=self.surface,
            #                                  thickness_parameters=self.settings.thickness_parameters,
            #                                  positive_direction=True)
            # for point in offset_path_upper.points:
            #     self.svg_strokes.append(svgwrite.shapes.Circle((point[0], point[1]), r=0.5, fill="magenta"))
            #
            # offset_path_lower = curve.offset(interval=self.settings.curve_sampling_interval,
            #                                  surface=self.surface,
            #                                  thickness_parameters=self.settings.thickness_parameters,
            #                                  positive_direction=False)
            # for point in offset_path_lower.points:
            #     self.svg_strokes.append(svgwrite.shapes.Circle((point[0], point[1]), r=0.5, fill="pink"))
            #
            # upper_curve = Curve1D(path=offset_path_upper, fit_error=self.settings.curve_fit_error)
            # svg_stroke = svgwrite.path.Path(stroke="blue", fill="none", stroke_width=0.2)
            # svg_stroke.push(upper_curve.d)
            # self.svg_strokes.append(svg_stroke)
            #
            # lower_curve = Curve1D(path=offset_path_lower, fit_error=self.settings.curve_fit_error)
            # svg_stroke = svgwrite.path.Path(stroke="teal", fill="none", stroke_width=0.2)
            # svg_stroke.push(lower_curve.d)
            # self.svg_strokes.append(svg_stroke)
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
            norm_image_component = self.surface.norm_x_image
            logger.debug("Creating (u) streamline at intensity %d...", intensity)
            u_streamline = Streamline(primary_uv_image_component=u_image,
                                      secondary_uv_image_component=v_image,
                                      norm_image_component=norm_image_component,
                                      surface=self.surface,
                                      intensity=intensity,
                                      settings=self.settings)
            u_streamline.generate()
            strokes += u_streamline.strokes

            # # TODO: For debug visualisation only.
            # for path in u_streamline.paths:
            #     for point in path.points:
            #         self.svg_strokes.append(svgwrite.shapes.Circle((str(point[0]), str(point[1])), r=2, fill="red"))

        for intensity in v_intensities:
            norm_image_component = self.surface.norm_y_image
            logger.debug("Creating (v) streamline at intensity %d...", intensity)
            v_streamline = Streamline(primary_uv_image_component=v_image,
                                      secondary_uv_image_component=u_image,
                                      norm_image_component=norm_image_component,
                                      surface=self.surface,
                                      intensity=intensity,
                                      settings=self.settings)
            v_streamline.generate()
            strokes += v_streamline.strokes

            # # TODO: For debug visualisation only.
            # for path in v_streamline.paths:
            #     for point in path.points:
            #         self.svg_strokes.append(svgwrite.shapes.Circle((str(point[0]), str(point[1])), r=2, fill="green"))

        for stroke in strokes:
            svg_stroke = svgwrite.path.Path(fill=self.settings.stroke_colour, stroke_width=0)
            svg_stroke.push(stroke.d)
            self.svg_strokes.append(svg_stroke)

            # for point in stroke.upper_curve.path.points:
            #     self.svg_strokes.append(svgwrite.shapes.Circle((point[0], point[1]), r=1, fill="magenta"))

        logger.info("Streamline Strokes prepared: %d", len(self.svg_strokes))


class Streamline:
    """
    A Streamline is a collection of Strokes which follow a specified UV intensity value.
    """

    def __init__(self, primary_uv_image_component, secondary_uv_image_component, norm_image_component,
                 surface, intensity, settings):
        self.primary_uv_image_component = primary_uv_image_component
        self.secondary_uv_image_component = secondary_uv_image_component
        self.norm_image_component = norm_image_component
        self.surface = surface
        self.intensity = intensity
        self.settings = settings

        self.paths = []
        self.strokes = []

    def generate(self):
        contours = measure.find_contours(self.primary_uv_image_component, self.intensity)
        logger.debug("Streamline contours found: %d", len(contours))

        for contour in contours:
            # Create the rough path.
            path = Path([[coord[1], coord[0]] for coord in contour])
            # Condition and create final paths.
            paths = path.round().bump(self.surface).remove_dupes().trim_uv(target_intensity=self.intensity,
                                                                           primary_image=self.primary_uv_image_component,
                                                                           secondary_image=self.secondary_uv_image_component,
                                                                           primary_trim_size=self.settings.uv_primary_trim_size,
                                                                           secondary_trim_size=self.settings.uv_secondary_trim_size)

            for path in paths:
                logger.debug("UV contour split into %d paths.", len(paths))

                hifi_path = path.simple_cull(self.settings.cull_factor)
                fit_path = hifi_path.optimise(self.settings.optimise_factor)

                num_points = len(fit_path.points)
                if num_points > 1:

                    # Store to allow plotting of construction points for debugging.
                    self.paths.append(fit_path)

                    stroke = create_stroke(fit_path=fit_path,
                                           hifi_path=hifi_path,
                                           thickness_parameters=self.settings.streamline_thickness_parameters,
                                           surface=self.surface,
                                           settings=self.settings)

                    self.strokes.append(stroke)
                else:
                    logger.debug("Streamline of length %d rejected", num_points)


if __name__ == "__main__":
    pass
