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
        if path.find_corners(self.surface.obj_image, self.settings.harris_min_distance, None):
            self.paths += path.split_corners()
        else:
            self.paths.append(path)

        logger.info("Silhouette Paths found: %d", len(self.paths))

        for path in self.paths:
            path.bump(self.surface)

            # TODO: Have an entry for this in settings.
            thickness_parameters = ThicknessParameters(const=0, z=0, diffdir=1, curvature=0)
            path.compute_thicknesses(self.surface, thickness_parameters)

            stroke = create_stroke(path=path, settings=self.settings)
            svg_stroke = svgwrite.path.Path(fill=self.settings.stroke_colour, stroke_width=0)
            svg_stroke.push(stroke.d)
            self.svg_strokes.append(svg_stroke)

            # TODO: THIS BLOCK IS FOR TESTING, PLOTS THE CONSTRUCTION CURVE.
            construction_curve = Curve1D(path=path,
                                         optimisation_factor=self.settings.rdp_epsilon,
                                         fit_error=self.settings.curve_fit_error)
            svg_stroke = svgwrite.path.Path(stroke="red", stroke_width=0.25, fill="none")
            svg_stroke.push(construction_curve.d)
            self.svg_strokes.append(svg_stroke)

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
            thickness_parameters = ThicknessParameters(const=0, z=0, diffdir=0, curvature=0.01)
            path.compute_thicknesses(self.surface, thickness_parameters)
            # self.surface.compute_curvature(path, self.primary_image)

            # threshold = 0.0005
            # first_derivatives = []
            # for i in range(0, len(path.points) - 1):
            #     cur = self.surface.at_point(path.points[i][0], path.points[i][1]).norm
            #     next = self.surface.at_point(path.points[i + 1][0], path.points[i + 1][1]).norm
            #
            #     delta = abs(cur - next)
            #     if delta > threshold:
            #         first_derivatives.append(delta)
            #     else:
            #         first_derivatives.append(0)
            #
            # # def compute_thing(list):
            # #     indices = []
            # #     for i, element in enumerate(list):
            # #         if element > 0:
            # #             indices.append(i)
            # #     print(indices)
            # #
            # #     distances = []
            # #     for i in range(0, len(indices) - 1):
            # #         distance = indices[i + 1] - indices[i]
            # #         distances.append(distance)
            # #
            # #     from statistics import mode, mean, median
            # #
            # #     buffer_factor = 1.5
            # #
            # #     return int(round(mode(distances) * buffer_factor))
            #
            # def interpolate(vals):
            #     import numpy as np
            #     from scipy.interpolate import interp1d
            #
            #     vals = np.array(vals)
            #     nonzero_idx = np.nonzero(vals)
            #     nonzero_vals = vals[nonzero_idx]
            #
            #     out = []
            #     # Pad start with zeros as needed.
            #     for i in range(0, nonzero_idx[0][0]):
            #         out.append(0)
            #
            #     interp = interp1d(nonzero_idx[0], nonzero_vals)
            #     out += [interp(x) for x in range(nonzero_idx[0][0], nonzero_idx[0][-1] + 1)]
            #
            #     # Pad end with zeros as needed.
            #     for i in range(nonzero_idx[0][-1], len(vals)):
            #         out.append(0)
            #
            #     return out
            #
            # first_derivatives_new = interpolate(first_derivatives)
            #
            # from matplotlib import pyplot
            # import numpy as np
            # pyplot.plot(first_derivatives)
            # pyplot.plot(first_derivatives_new)
            # pyplot.show()
            #
            # self.paths.append(path)  # For viz only.
            # print(len(path.points))
            # print(len(first_derivatives_new))

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
