import logging
import os

import svgwrite

from blender_hand_drawn_npr.silhouette import Silhouette
from blender_hand_drawn_npr.surface import Surface

logger = logging.getLogger(__name__)


class Illustrator:

    def __init__(self, img_dir, out_filename):
        self.img_dir = img_dir
        self.out_filename = out_filename

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
        silhouette = Silhouette(self.surface)
        silhouette.generate()

        [self.illustration.add(stroke.svg_path) for stroke in silhouette.strokes]

    def save(self):
        self.illustration.save()

        logger.info("Illustration saved to: %s", os.path.join(self.img_dir, self.out_filename))


if __name__ == "__main__":
    illustrator = Illustrator("/tmp/undulating_plane", "Illustration.svg")
    illustrator.illustrate()
    illustrator.save()
