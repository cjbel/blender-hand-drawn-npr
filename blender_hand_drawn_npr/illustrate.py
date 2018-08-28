import logging
import os

import svgwrite

from blender_hand_drawn_npr.elements import Silhouette, InternalEdges, Streamlines, Stipples
from blender_hand_drawn_npr.models import Surface
from blender_hand_drawn_npr.primitives import Settings, ThicknessParameters, LightingParameters, StippleParameters

logger = logging.getLogger(__name__)


class Illustrator:

    def __init__(self, settings):
        self.settings = settings

        self.surface = Surface()
        self.surface.init_obj_image(os.path.join(self.settings.in_path, "IndexOB0001.png"))
        self.surface.init_z_image(os.path.join(self.settings.in_path, "Depth0001.png"))
        self.surface.init_diffdir_image(os.path.join(self.settings.in_path, "DiffDir0001.png"))
        self.surface.init_norm_image(os.path.join(self.settings.in_path, "Normal0001.tif"))
        self.surface.init_uv_image(os.path.join(self.settings.in_path, "UV0001.tif"))
        self.surface.init_shadow_image(os.path.join(self.settings.in_path, "Shadow0001.png"))
        self.surface.init_ao_image(os.path.join(self.settings.in_path, "AO0001.png"))

        illustration_dimensions = (self.surface.obj_image.shape[1],
                                   self.surface.obj_image.shape[0])
        self.illustration = svgwrite.Drawing(os.path.join(self.settings.in_path, self.settings.out_filename),
                                             illustration_dimensions)

        self.intersect_boundaries = []

    def illustrate(self):
        silhouette = Silhouette(surface=self.surface, settings=self.settings)
        silhouette.generate()
        [self.illustration.add(svg_stroke) for svg_stroke in silhouette.svg_strokes]
        [self.intersect_boundaries.append(boundary_curve) for boundary_curve in silhouette.boundary_curves]
        clip_path = self.illustration.defs.add(self.illustration.clipPath(id='silhouette_clip_path'))
        clip_path.add(svgwrite.path.Path(silhouette.clip_path_d))

        if self.settings.enable_internal_edges:
            internal_edges = InternalEdges(surface=self.surface, settings=self.settings)
            internal_edges.generate()
            [self.illustration.add(svg_stroke) for svg_stroke in internal_edges.svg_strokes]

        if self.settings.enable_streamlines:
            streamlines = Streamlines(surface=self.surface, settings=self.settings)
            streamlines.generate()
            [self.illustration.add(svg_stroke) for svg_stroke in streamlines.svg_strokes]

        if self.settings.enable_stipples:
            stipples = Stipples(clip_path=clip_path, intersect_boundaries=self.intersect_boundaries,
                                surface=self.surface, settings=self.settings)
            stipples.generate()
            [self.illustration.add(svg_stroke) for svg_stroke in stipples.svg_strokes]

    def save(self):
        self.illustration.save()

        logger.info("Illustration saved to: %s", os.path.join(self.settings.in_path, self.settings.out_filename))


if __name__ == "__main__":
    # illustrator = Illustrator("/tmp/hyperbolic_paraboloid_xy", "Illustration.svg")
    # illustrator = Illustrator("/tmp/hyperbolic_paraboloid_xy_scaledx", "Illustration.svg")
    # illustrator = Illustrator("/tmp/hyperbolic_paraboloid_polar", "Illustration.svg")
    # illustrator = Illustrator("/tmp/catenoid", "Illustration.svg")
    # illustrator = Illustrator("/tmp/cosinus", "Illustration.svg")
    # illustrator = Illustrator("/tmp/undulating_plane", "Illustration.svg")
    # illustrator = Illustrator("/tmp/bump_plane_ortho_uv", "Illustration.svg")
    # illustrator = Illustrator("/tmp/teapot", "Illustration.svg")
    # illustrator = Illustrator("/tmp/thinker", "Illustration.svg")
    # illustrator = Illustrator("/tmp/taranaki", "Illustration.svg")
    # illustrator = Illustrator("/tmp/human", "Illustration.svg")
    # illustrator = Illustrator("/tmp/brooklynbridge", "Illustration.svg")
    # illustrator = Illustrator("/tmp/lion", "Illustration.svg")
    # illustrator = Illustrator("/tmp/colosseum", "Illustration.svg")
    illustrator.illustrate()
    illustrator.save()
