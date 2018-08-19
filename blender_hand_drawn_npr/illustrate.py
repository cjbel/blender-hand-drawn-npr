import logging
import os

import svgwrite

from blender_hand_drawn_npr.elements import Silhouette, InternalEdges
from blender_hand_drawn_npr.models import Surface
from blender_hand_drawn_npr.primitives import Settings, ThicknessParameters, LightingParameters, StippleParameters

logger = logging.getLogger(__name__)


class Illustrator:

    def __init__(self, img_dir, out_filename):
        self.img_dir = img_dir
        self.out_filename = out_filename

        # Hyperbolic Paraboloid.
        self.settings = Settings(cull_factor=50,
                                 optimise_factor=5,
                                 curve_fit_error=0.01,
                                 harris_min_distance=40,
                                 subpix_window_size=20,
                                 curve_sampling_interval=20,
                                 stroke_colour="black",
                                 streamline_segments=32,
                                 silhouette_thickness_parameters=ThicknessParameters(const=0.05, z=5, diffdir=0,
                                                                                     stroke_curvature=0),
                                 internal_edge_thickness_parameters=ThicknessParameters(const=0.05, z=5, diffdir=0,
                                                                                        stroke_curvature=0),
                                 streamline_thickness_parameters=ThicknessParameters(const=0.01, z=0.1, diffdir=0,
                                                                                     stroke_curvature=50),
                                 uv_primary_trim_size=200,
                                 uv_secondary_trim_size=20,
                                 lighting_parameters=LightingParameters(diffdir=0, shadow=1, ao=1,
                                                                        threshold=0.3),
                                 stipple_parameters=StippleParameters(head_radius=0.8, tail_radius=0, length=10,
                                                                      density_fn_min=0.0005,
                                                                      density_fn_factor=0.0025,
                                                                      density_fn_exponent=3),
                                 optimise_clip_paths=True)

        # Human.
        # self.settings = Settings(cull_factor=50,
        #                          optimise_factor=5,
        #                          curve_fit_error=0.01,
        #                          harris_min_distance=40,
        #                          subpix_window_size=20,
        #                          curve_sampling_interval=20,
        #                          stroke_colour="black",
        #                          streamline_segments=128,
        #                          silhouette_thickness_parameters=ThicknessParameters(const=0.05, z=5, diffdir=0,
        #                                                                              stroke_curvature=0),
        #                          internal_edge_thickness_parameters=ThicknessParameters(const=0.2, z=0, diffdir=0,
        #                                                                                 stroke_curvature=0),
        #                          streamline_thickness_parameters=ThicknessParameters(const=0.001, z=0.2, diffdir=0,
        #                                                                              stroke_curvature=0),
        #                          uv_primary_trim_size=200,
        #                          uv_secondary_trim_size=20,
        #                          lighting_parameters=LightingParameters(diffdir=1, shadow=2, ao=3,
        #                                                                 threshold=0.2),
        #                          stipple_parameters=StippleParameters(head_radius=0.8, tail_radius=0, length=30,
        #                                                               density_fn_min=0.0005,
        #                                                               density_fn_factor=0.0025,
        #                                                               density_fn_exponent=3),
        #                          optimise_clip_paths=True)

        self.surface = Surface()
        self.surface.init_obj_image(os.path.join(self.img_dir, "IndexOB0001.png"))
        self.surface.init_z_image(os.path.join(self.img_dir, "Depth0001.png"))
        self.surface.init_diffdir_image(os.path.join(self.img_dir, "DiffDir0001.png"))
        self.surface.init_norm_image(os.path.join(self.img_dir, "Normal0001.tif"))
        self.surface.init_uv_image(os.path.join(self.img_dir, "UV0001.tif"))
        self.surface.init_shadow_image(os.path.join(self.img_dir, "Shadow0001.png"))
        self.surface.init_ao_image(os.path.join(self.img_dir, "AO0001.png"))

        illustration_dimensions = (self.surface.obj_image.shape[1],
                                   self.surface.obj_image.shape[0])
        self.illustration = svgwrite.Drawing(os.path.join(self.img_dir, self.out_filename), illustration_dimensions)

        self.intersect_boundaries = []

    def illustrate(self):
        silhouette = Silhouette(surface=self.surface, settings=self.settings)
        silhouette.generate()
        [self.illustration.add(svg_stroke) for svg_stroke in silhouette.svg_strokes]
        [self.intersect_boundaries.append(boundary_curve) for boundary_curve in silhouette.boundary_curves]
        clip_path = self.illustration.defs.add(self.illustration.clipPath(id='silhouette_clip_path'))
        clip_path.add(svgwrite.path.Path(silhouette.clip_path_d))

        internal_edges = InternalEdges(surface=self.surface, settings=self.settings)
        internal_edges.generate()
        [self.illustration.add(svg_stroke) for svg_stroke in internal_edges.svg_strokes]

        # streamlines = Streamlines(surface=self.surface, settings=self.settings)
        # streamlines.generate()
        # [self.illustration.add(svg_stroke) for svg_stroke in streamlines.svg_strokes]
        #
        # stipples = Stipples(clip_path=clip_path, intersect_boundaries=self.intersect_boundaries,
        #                     surface=self.surface, settings=self.settings)
        # stipples.generate()
        # [self.illustration.add(svg_stroke) for svg_stroke in stipples.svg_strokes]

    def save(self):
        self.illustration.save()

        logger.info("Illustration saved to: %s", os.path.join(self.img_dir, self.out_filename))


if __name__ == "__main__":
    # illustrator = Illustrator("/tmp/undulating_plane", "Illustration.svg")
    # illustrator = Illustrator("/tmp/test", "Illustration.svg")
    # illustrator = Illustrator("/tmp/bump", "Illustration.svg")
    # illustrator = Illustrator("/tmp/flat", "Illustration.svg")
    # illustrator = Illustrator("/tmp/sphere", "Illustration.svg")
    illustrator = Illustrator("/tmp/hyperbolic_paraboloid_xy", "Illustration.svg")
    # illustrator = Illustrator("/tmp/surface_1D_curvature", "Illustration.svg")
    # illustrator = Illustrator("/tmp/bump_plane_ortho_uv", "Illustration.svg")
    # illustrator = Illustrator("/tmp/human", "Illustration.svg")
    illustrator.illustrate()
    illustrator.save()
