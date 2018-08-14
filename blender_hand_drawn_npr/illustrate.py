import logging
import os

import svgwrite

from blender_hand_drawn_npr.elements import Silhouette, Streamlines
from blender_hand_drawn_npr.models import Surface
from blender_hand_drawn_npr.primitives import Settings, ThicknessParameters

logger = logging.getLogger(__name__)


class Illustrator:

    def __init__(self, img_dir, out_filename):
        self.img_dir = img_dir
        self.out_filename = out_filename

        # # Flat. Issue with corner detection on far end.
        # self.settings = Settings(rdp_epsilon=50,
        #                          curve_fit_error=0.01,
        #                          harris_min_distance=40,
        #                          subpix_window_size=20,
        #                          curve_sampling_interval=50,
        #                          thickness_model=None,
        #                          stroke_colour="black",
        #                          streamline_segments=16,
        #                          thickness_parameters=None,
        #                          uv_allowable_deviance=30)
        #
        # # Bump.
        # self.settings = Settings(rdp_epsilon=50,
        #                          curve_fit_error=0.01,
        #                          harris_min_distance=100,
        #                          subpix_window_size=50,
        #                          curve_sampling_interval=50,
        #                          thickness_model=None,
        #                          stroke_colour="black",
        #                          streamline_segments=16,
        #                          thickness_parameters=None,
        #                          uv_allowable_deviance=30)

        # Undulating plane.
        self.settings = Settings(rdp_epsilon=5,
                                 curve_fit_error=0.001,
                                 harris_min_distance=40,
                                 subpix_window_size=20,
                                 curve_sampling_interval=10,
                                 stroke_colour="black",
                                 streamline_segments=2,
                                 thickness_parameters=ThicknessParameters(const=0.1, z=0, diffdir=0, curvature=0),
                                 uv_allowable_deviance=40)

        self.surface = Surface()
        self.surface.init_obj_image(os.path.join(self.img_dir, "IndexOB0001.png"))
        self.surface.init_z_image(os.path.join(self.img_dir, "Depth0001.png"))
        self.surface.init_diffdir_image(os.path.join(self.img_dir, "DiffDir0001.png"))
        self.surface.init_norm_image(os.path.join(self.img_dir, "Normal0001.tif"))
        self.surface.init_uv_image(os.path.join(self.img_dir, "UV0001.tif"))

        illustration_dimensions = (self.surface.obj_image.shape[1],
                                   self.surface.obj_image.shape[0])
        self.illustration = svgwrite.Drawing(os.path.join(self.img_dir, self.out_filename), illustration_dimensions)

    def illustrate(self):
        silhouette = Silhouette(surface=self.surface, settings=self.settings)
        silhouette.generate()
        [self.illustration.add(svg_stroke) for svg_stroke in silhouette.svg_strokes]

        # streamlines = Streamlines(surface=self.surface, settings=self.settings)
        # streamlines.generate()
        # [self.illustration.add(svg_stroke) for svg_stroke in streamlines.svg_strokes]

        # from skimage import io
        # io.imsave("/tmp/curvature.png", self.surface.u_curvature_image)

    def save(self):
        self.illustration.save()

        logger.info("Illustration saved to: %s", os.path.join(self.img_dir, self.out_filename))


if __name__ == "__main__":
    illustrator = Illustrator("/tmp/undulating_plane", "Illustration.svg")
    # illustrator = Illustrator("/tmp/bump", "Illustration.svg")
    # illustrator = Illustrator("/tmp/flat", "Illustration.svg")
    # illustrator = Illustrator("/tmp/sphere", "Illustration.svg")
    # illustrator = Illustrator("/tmp/bump_plane_ortho_uv", "Illustration.svg")
    # illustrator = Illustrator("/tmp/surface_1D_curvature", "Illustration.svg")
    illustrator.illustrate()
    illustrator.save()
