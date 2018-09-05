# if "bpy" in locals():
#     import importlib
# else:
#     try:
#         from .core.illustrate import Illustrator
#         from .core.models import Settings, ThicknessParameters, LightingParameters, StippleParameters
#     except (AttributeError, ImportError):
#         print("Core imports failed!")
#         # This will fail when being called from vanilla Blender during tests due to lack of needed dependencies.
#         # This is fine, since only the internal Blender functionality is tested.
#
# import bpy
# import os
# import tempfile
# import logging
# from bpy.app.handlers import persistent
#
# logger = logging.getLogger(__name__)
#
# # Define expected render passes.
# pass_names = [
#     "Image",
#     "Depth",
#     "Normal",
#     "UV",
#     "Shadow",
#     "AO",
#     "IndexOB",
#     "DiffDir"
# ]
#
#
#
#
# def render(dummy):
#     # context = bpy.context
#     # system_settings = context.scene.system_settings
#     #
#     # try:
#     #     logger.debug("Building settings...")
#     #
#     #     silhouette_thickness_parameters = ThicknessParameters(const=system_settings.silhouette_const,
#     #                                                           z=system_settings.silhouette_depth,
#     #                                                           diffdir=system_settings.silhouette_diffuse,
#     #                                                           stroke_curvature=system_settings.silhouette_curvature)
#     #     internal_edge_thickness_parameters = ThicknessParameters(const=system_settings.internal_const,
#     #                                                              z=system_settings.internal_depth,
#     #                                                              diffdir=system_settings.internal_diffuse,
#     #                                                              stroke_curvature=system_settings.internal_curvature)
#     #     streamline_thickness_parameters = ThicknessParameters(const=system_settings.streamline_const,
#     #                                                           z=system_settings.streamline_depth,
#     #                                                           diffdir=system_settings.streamline_diffuse,
#     #                                                           stroke_curvature=system_settings.streamline_curvature)
#     #     lighting_parameters = LightingParameters(diffdir=system_settings.stipple_diffuse,
#     #                                              shadow=system_settings.stipple_shadow,
#     #                                              ao=system_settings.stipple_ao,
#     #                                              threshold=system_settings.stipple_threshold / 100)
#     #     stipple_parameters = StippleParameters(head_radius=system_settings.stipple_head_radius,
#     #                                            tail_radius=system_settings.stipple_tail_radius,
#     #                                            length=system_settings.stipple_length,
#     #                                            density_fn_min=system_settings.stipple_min_allowable,
#     #                                            density_fn_factor=system_settings.stipple_density_factor,
#     #                                            density_fn_exponent=system_settings.stipple_density_exponent)
#     #
#     #     settings = Settings(in_path=tempfile.gettempdir(),
#     #                         out_filename=system_settings.out_filename,
#     #                         harris_min_distance=system_settings.corner_factor,
#     #                         silhouette_thickness_parameters=silhouette_thickness_parameters,
#     #                         enable_internal_edges=system_settings.is_internal_enabled,
#     #                         internal_edge_thickness_parameters=internal_edge_thickness_parameters,
#     #                         enable_streamlines=system_settings.is_streamlines_enabled,
#     #                         streamline_segments=system_settings.streamline_segments,
#     #                         streamline_thickness_parameters=streamline_thickness_parameters,
#     #                         enable_stipples=system_settings.is_stipples_enabled,
#     #                         lighting_parameters=lighting_parameters,
#     #                         stipple_parameters=stipple_parameters,
#     #                         optimise_clip_paths=system_settings.is_optimisation_enabled,
#     #                         # Note: Remaining values hard-coded to sensible defaults. Minimal benefit to exposing
#     #                         # these in UI.
#     #                         cull_factor=20,
#     #                         optimise_factor=5,
#     #                         curve_fit_error=0.01,
#     #                         subpix_window_size=20,
#     #                         curve_sampling_interval=20,
#     #                         stroke_colour="black",
#     #                         uv_primary_trim_size=200,
#     #                         uv_secondary_trim_size=20)
#     #
#     #     logger.debug("Starting illustrator...")
#     #     illustrator = Illustrator(settings)
#     #
#     # except (NameError):
#     #     # This will fail when being called from vanilla Blender during tests due to lack of needed dependencies.
#     #     # Bail out here, since only the internal Blender functionality is tested.
#     #     logger.warning("process_illustration threw exception!")
#     #     return
#     #
#     # logger.debug("Processing Illustration...")
#     # illustrator.illustrate()
#     # illustrator.save()
#
#
# # def register():
# #     logger.debug("Registering classes...")
# #
# #     from .view_controller import operators
# #     from .view_controller import properties
# #     from .view_controller import ui
# #
# #     operators.register()
# #     properties.register()
# #     ui.register()
# #
# #     # bpy.utils.register_class(CreateCompositorNodeOperator)
# #     # bpy.utils.register_class(DestroyCompositorNodeOperator)
# #     # bpy.utils.register_class(MainPanel)
# #     # bpy.utils.register_class(NPRSystemSettings)
# #     #
# #     # bpy.types.Scene.system_settings = bpy.props.PointerProperty(type=NPRSystemSettings)
# #
# #
# # def unregister():
# #     logger.debug("Unregistering classes...")
# #
# #     from .view_controller import operators
# #     from .view_controller import properties
# #     from .view_controller import ui
# #
# #     operators.unregister()
# #     properties.unregister()
# #     ui.unregister()
# #
# #     # bpy.utils.unregister_class(CreateCompositorNodeOperator)
# #     # bpy.utils.unregister_class(DestroyCompositorNodeOperator)
# #     # bpy.utils.unregister_class(MainPanel)
# #     # bpy.utils.unregister_class(NPRSystemSettings)
# #     # del bpy.types.Scene.system_settings
#
#
# if __name__ == "__main__":
#     register()
