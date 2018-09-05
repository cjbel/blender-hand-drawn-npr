import logging

import bpy

logger = logging.getLogger(__name__)


def toggle_hook(self, context):

    if context.scene.system_settings.is_hook_enabled:
        logger.debug("Enabling hook...")
        bpy.app.handlers.render_post.append(render)
    else:
        logger.debug("Disabling hook...")
        bpy.app.handlers.render_post.remove(render)


def render(dummy):

    bpy.ops.wm.prepare_npr_settings()
    bpy.ops.wm.create_npr_compositor_nodes()

    logger.debug("Executing RenderNPR...")

    context = bpy.context
    system_settings = context.scene.system_settings

    logger.debug("Building settings...")

    silhouette_thickness_parameters = ThicknessParameters(const=system_settings.silhouette_const,
                                                          z=system_settings.silhouette_depth,
                                                          diffdir=system_settings.silhouette_diffuse,
                                                          stroke_curvature=system_settings.silhouette_curvature)
    internal_edge_thickness_parameters = ThicknessParameters(const=system_settings.internal_const,
                                                             z=system_settings.internal_depth,
                                                             diffdir=system_settings.internal_diffuse,
                                                             stroke_curvature=system_settings.internal_curvature)
    streamline_thickness_parameters = ThicknessParameters(const=system_settings.streamline_const,
                                                          z=system_settings.streamline_depth,
                                                          diffdir=system_settings.streamline_diffuse,
                                                          stroke_curvature=system_settings.streamline_curvature)
    lighting_parameters = LightingParameters(diffdir=system_settings.stipple_diffuse,
                                             shadow=system_settings.stipple_shadow,
                                             ao=system_settings.stipple_ao,
                                             threshold=system_settings.stipple_threshold / 100)
    stipple_parameters = StippleParameters(head_radius=system_settings.stipple_head_radius,
                                           tail_radius=system_settings.stipple_tail_radius,
                                           length=system_settings.stipple_length,
                                           density_fn_min=system_settings.stipple_min_allowable,
                                           density_fn_factor=system_settings.stipple_density_factor,
                                           density_fn_exponent=system_settings.stipple_density_exponent)

    settings = Settings(in_path=tempfile.gettempdir(),
                        out_filename=system_settings.out_filename,
                        harris_min_distance=system_settings.corner_factor,
                        silhouette_thickness_parameters=silhouette_thickness_parameters,
                        enable_internal_edges=system_settings.is_internal_enabled,
                        internal_edge_thickness_parameters=internal_edge_thickness_parameters,
                        enable_streamlines=system_settings.is_streamlines_enabled,
                        streamline_segments=system_settings.streamline_segments,
                        streamline_thickness_parameters=streamline_thickness_parameters,
                        enable_stipples=system_settings.is_stipples_enabled,
                        lighting_parameters=lighting_parameters,
                        stipple_parameters=stipple_parameters,
                        optimise_clip_paths=system_settings.is_optimisation_enabled,
                        # Note: Remaining values hard-coded to sensible defaults. Minimal benefit to exposing
                        # these in UI.
                        cull_factor=20,
                        optimise_factor=5,
                        curve_fit_error=0.01,
                        subpix_window_size=20,
                        curve_sampling_interval=20,
                        stroke_colour="black",
                        uv_primary_trim_size=200,
                        uv_secondary_trim_size=20)

    logger.debug("Starting illustrator...")
    illustrator = Illustrator(settings)
    illustrator.illustrate()
    illustrator.save()
