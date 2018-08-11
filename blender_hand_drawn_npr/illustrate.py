import logging
import os

import svgwrite

from blender_hand_drawn_npr.elements import Silhouette, Streamlines
from blender_hand_drawn_npr.models import Surface
from blender_hand_drawn_npr.primitives import Settings

logger = logging.getLogger(__name__)


class Illustrator:

    def __init__(self, img_dir, out_filename):
        self.img_dir = img_dir
        self.out_filename = out_filename

        self.settings = Settings(rdp_epsilon=0.1,
                                 curve_fit_error=0.01,
                                 harris_min_distance=50,
                                 curve_sampling_interval=100,
                                 thickness_model=None,
                                 stroke_colour="black",
                                 streamline_segments=5,
                                 thickness_parameters=None)

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
        # silhouette = Silhouette(surface=self.surface, settings=self.settings)
        # silhouette.generate()
        # [self.illustration.add(svg_stroke) for svg_stroke in silhouette.svg_strokes]

        streamlines = Streamlines(surface=self.surface, settings=self.settings)
        streamlines.generate()
        [self.illustration.add(svg_stroke) for svg_stroke in streamlines.svg_strokes]

        # from skimage import io
        # io.imsave("/tmp/curvature.png", self.surface.u_curvature_image)

    def save(self):
        self.illustration.save()

        logger.info("Illustration saved to: %s", os.path.join(self.img_dir, self.out_filename))


if __name__ == "__main__":
    illustrator = Illustrator("/tmp/undulating_plane", "Illustration.svg")
    # illustrator = Illustrator("/tmp/sphere", "Illustration.svg")
    # illustrator = Illustrator("/tmp/bump_plane_ortho_uv", "Illustration.svg")
    # illustrator = Illustrator("/tmp/surface_1D_curvature", "Illustration.svg")
    illustrator.illustrate()
    illustrator.illustrate()
    illustrator.save()
