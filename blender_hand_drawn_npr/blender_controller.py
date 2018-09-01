if "bpy" in locals():
    import importlib
else:
    try:
        from .core.illustrate import Illustrator
        from .core.models import Settings, ThicknessParameters, LightingParameters, StippleParameters
    except (ValueError):
    # except (AttributeError, ImportError):
        print("Core imports failed!")
        # This will fail when being called from vanilla Blender during tests due to lack of needed dependencies.
        # This is fine, since only the internal Blender functionality is tested.

import bpy
import os
import tempfile
import logging
from bpy.app.handlers import persistent

logger = logging.getLogger(__name__)

# Define expected render passes.
pass_names = [
    "Image",
    "Depth",
    "Normal",
    "UV",
    "Shadow",
    "AO",
    "IndexOB",
    "DiffDir"
]


def process_illustration(dummy):
    context = bpy.context
    system_settings = context.scene.system_settings

    try:
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

    except (NameError):
        # This will fail when being called from vanilla Blender during tests due to lack of needed dependencies.
        # Bail out here, since only the internal Blender functionality is tested.
        logger.warning("process_illustration threw exception!")
        return

    logger.debug("Processing Illustration...")
    illustrator.illustrate()
    illustrator.save()


def toggle_system(self, context):
    if context.scene.system_settings.is_system_enabled:
        logger.debug("Enabling system...")

        # Adjust configurations to suit the needs of the add-on.

        bpy.context.scene.render.engine = "CYCLES"

        # Set default resolution.
        bpy.context.scene.render.resolution_x = 3840
        bpy.context.scene.render.resolution_y = 2160
        bpy.context.scene.render.resolution_percentage = 100

        bpy.context.scene.frame_current = 1

        # By default, anti-aliasing is applied which wreaks havok with images which represent hard data
        # (e.g uv pass image). Most effective way to turn off AA is by using Branched Path Tracing and minimising
        # AA samples.
        bpy.context.scene.cycles.progressive = 'BRANCHED_PATH'
        bpy.context.scene.cycles.aa_samples = 1
        bpy.context.scene.cycles.preview_aa_samples = 0

        # Some sensible defaults.
        bpy.context.scene.cycles.diffuse_samples = 10
        bpy.context.scene.cycles.ao_samples = 10

        layer = bpy.context.scene.render.layers["RenderLayer"]
        logger.debug("Configuring passes for " + layer.name)
        layer.use_pass_normal = True
        layer.use_pass_uv = True
        layer.use_pass_object_index = True
        layer.use_pass_z = True
        layer.use_pass_diffuse_direct = True
        layer.use_pass_shadow = True
        layer.use_pass_ambient_occlusion = True

        bpy.ops.wm.create_npr_compositor_nodes()

        # Silhouette drawing needs knowledge of the corresponding grey level in the indexOB map, which is
        # based on this index.
        for object in context.scene.objects:
            if object.type == 'MESH':
                index = 1
                object.pass_index = index
                logger.debug("Assigned pass index %d to object: %s", index, object.name)

        bpy.app.handlers.render_post.append(process_illustration)
    else:
        logger.debug("Disabling system...")

        bpy.ops.wm.destroy_npr_compositor_nodes()

        bpy.app.handlers.render_post.remove(process_illustration)


class CreateCompositorNodeOperator(bpy.types.Operator):
    bl_idname = "wm.create_npr_compositor_nodes"
    bl_label = "Create compositor nodes to write render passes to disk."

    def execute(self, context):
        logger.debug("Executing CreateCompositorNodeOperator...")

        # Blender command for troubleshooting.
        # file_out_node = bpy.context.scene.node_tree.nodes[2]

        context.scene.use_nodes = True
        tree = bpy.context.scene.node_tree

        # Remove all nodes.
        for node in tree.nodes:
            tree.nodes.remove(node)

        # Create nodes.
        render_layer_node = tree.nodes.new(type="CompositorNodeRLayers")
        render_layer_node.location = 0, 0
        file_out_node = tree.nodes.new(type="CompositorNodeOutputFile")
        file_out_node.location = 440, 0
        normalise_node = tree.nodes.new(type="CompositorNodeNormalize")
        normalise_node.location = 220, 10

        # Configure image path.
        file_out_node.base_path = tempfile.gettempdir()

        # Configure outputs and link nodes.
        file_out_node.file_slots.clear()
        links = tree.links
        for pass_name in pass_names:
            file_out_node.file_slots.new(name=pass_name)
            if pass_name == "Depth":
                links.new(render_layer_node.outputs[pass_name], normalise_node.inputs[0])
                links.new(normalise_node.outputs[0], file_out_node.inputs[pass_name])
            else:
                links.new(render_layer_node.outputs[pass_name], file_out_node.inputs[pass_name])

        # Configure required image formats.
        file_out_node.format.compression = 0
        file_out_node.format.color_depth = "8"

        # Need to use tiff for 16-bit colour depth.
        file_out_node.file_slots['Normal'].use_node_format = False
        file_out_node.file_slots['Normal'].format.file_format = 'TIFF'
        file_out_node.file_slots['Normal'].format.color_depth = "16"
        file_out_node.file_slots['Normal'].format.tiff_codec = 'NONE'

        file_out_node.file_slots['UV'].use_node_format = False
        file_out_node.file_slots['UV'].format.file_format = 'TIFF'
        file_out_node.file_slots['UV'].format.color_depth = "16"
        file_out_node.file_slots['UV'].format.tiff_codec = 'NONE'

        return {'FINISHED'}


class DestroyCompositorNodeOperator(bpy.types.Operator):
    bl_idname = "wm.destroy_npr_compositor_nodes"
    bl_label = "Destroy compositor nodes to write render passes to disk."

    def execute(self, context):
        logger.debug("Executing DestroyCompositorNodeOperator...")

        return {'FINISHED'}


class NPRSystemSettings(bpy.types.PropertyGroup):
    """ Define add-on system settings. """

    logger.debug("Instantiating SystemSettings...")

    is_system_enabled = bpy.props.BoolProperty(name="Enable",
                                               description="Draw stylised strokes using Hand Drawn NPR",
                                               default=False,
                                               update=toggle_system)

    out_filename = bpy.props.StringProperty(name="",
                                            description="File path for the produced SVG",
                                            default=os.path.join(tempfile.gettempdir(), "out.svg"),
                                            subtype="FILE_PATH")

    corner_factor = bpy.props.IntProperty(name="Corner Factor",
                                          description="Influences sensitivity of corner detection. Specifically, "
                                                      "this value influences the min_distance parameter of skimage "
                                                      "peak_local_max",
                                          default=40,
                                          min=1,
                                          soft_max=1000)

    silhouette_const = bpy.props.FloatProperty(name="Constant",
                                               description="Apply a constant thickness to silhouette lines. Thickness "
                                                           "will be proportional to the specified factor",
                                               precision=1,
                                               default=1,
                                               min=0,
                                               soft_max=10)

    silhouette_depth = bpy.props.FloatProperty(name="Depth",
                                               description="Vary silhouette line weight according to distance from the "
                                                           "camera. Thickness will be proportional to the specified "
                                                           "factor",
                                               precision=1,
                                               default=0,
                                               min=0,
                                               soft_max=10)

    silhouette_diffuse = bpy.props.FloatProperty(name="Diffuse",
                                                 description="Vary silhouette line weight according to direct diffuse "
                                                             "lighting. Thickness will be proportional to the "
                                                             "specified factor",
                                                 precision=1,
                                                 default=0,
                                                 min=0,
                                                 soft_max=10)

    silhouette_curvature = bpy.props.FloatProperty(name="Curvature",
                                                   description="Vary silhouette line weight according to line "
                                                               "curvature. Thickness will be proportional to the "
                                                               "specified factor",
                                                   precision=1,
                                                   default=0,
                                                   min=0,
                                                   soft_max=100)

    is_internal_enabled = bpy.props.BoolProperty(name="Internal Edges",
                                                 description="Enable internal edge lines",
                                                 default=False)

    internal_const = bpy.props.FloatProperty(name="Constant",
                                             description="Apply a constant thickness to internal edge lines. Thickness "
                                                         "will be proportional to the specified factor",
                                             precision=1,
                                             default=1,
                                             min=0,
                                             soft_max=10)

    internal_depth = bpy.props.FloatProperty(name="Depth",
                                             description="Vary internal edge line weight according to distance from the "
                                                         "camera. Thickness will be proportional to the specified "
                                                         "factor",
                                             precision=1,
                                             default=0,
                                             min=0,
                                             soft_max=10)

    internal_diffuse = bpy.props.FloatProperty(name="Diffuse",
                                               description="Vary internal edge line weight according to direct diffuse "
                                                           "lighting. Thickness will be proportional to the "
                                                           "specified factor",
                                               precision=1,
                                               default=0,
                                               min=0,
                                               soft_max=10)

    internal_curvature = bpy.props.FloatProperty(name="Curvature",
                                                 description="Vary internal edge line weight according to line "
                                                             "curvature. Thickness will be proportional to the "
                                                             "specified factor",
                                                 precision=1,
                                                 default=0,
                                                 min=0,
                                                 soft_max=100)

    is_streamlines_enabled = bpy.props.BoolProperty(name="Streamlines",
                                                    description="Enable streamlines (requires UV unwrapped mesh)",
                                                    default=False)

    streamline_const = bpy.props.FloatProperty(name="Constant",
                                               description="Apply a constant thickness to streamlines. Thickness "
                                                           "will be proportional to the specified factor",
                                               precision=1,
                                               default=1,
                                               min=0,
                                               soft_max=10)

    streamline_depth = bpy.props.FloatProperty(name="Depth",
                                               description="Vary streamline weight according to distance from the "
                                                           "camera. Thickness will be proportional to the specified "
                                                           "factor",
                                               precision=1,
                                               default=0,
                                               min=0,
                                               soft_max=10)

    streamline_diffuse = bpy.props.FloatProperty(name="Diffuse",
                                                 description="Vary streamline weight according to direct diffuse "
                                                             "lighting. Thickness will be proportional to the "
                                                             "specified factor",
                                                 precision=1,
                                                 default=0,
                                                 min=0,
                                                 soft_max=10)

    streamline_curvature = bpy.props.FloatProperty(name="Curvature",
                                                   description="Vary streamline weight according to line "
                                                               "curvature. Thickness will be proportional to the "
                                                               "specified factor",
                                                   precision=1,
                                                   default=0,
                                                   min=0,
                                                   soft_max=100)

    streamline_segments = bpy.props.IntProperty(name="Segments",
                                                description="The number of segments into which streamlines should "
                                                            "divide the mesh",
                                                default=16,
                                                min=2,
                                                soft_max=128)

    is_stipples_enabled = bpy.props.BoolProperty(name="Stipples",
                                                 description="Enable stipples (requires UV unwrapped mesh)",
                                                 default=False)

    is_optimisation_enabled = bpy.props.BoolProperty(name="Optimise Clip Path",
                                                     description="When enabled, each stipple is checked for "
                                                                 "intersection with a silhouette line. Only "
                                                                 "intersecting strokes are given a clip path. This "
                                                                 "greatly improves performance when opening the final "
                                                                 "image in an SVG editor, but comes "
                                                                 "with a performance penalty during rendering",
                                                     default=False)

    stipple_threshold = bpy.props.FloatProperty(name="Threshold",
                                                description="Stipples located on faces below this lighting intensity"
                                                            "threshold will be discarded.",
                                                precision=2,
                                                default=0,
                                                min=0,
                                                max=100,
                                                subtype="PERCENTAGE")

    stipple_diffuse = bpy.props.FloatProperty(name="Diffuse",
                                              description="Desired weighting of diffuse light contribution to the "
                                                          "overall lighting",
                                              precision=1,
                                              default=1,
                                              min=0,
                                              soft_max=10)

    stipple_shadow = bpy.props.FloatProperty(name="Shadow",
                                             description="Desired weighting of shadow contribution to the "
                                                         "overall lighting",
                                             precision=1,
                                             default=1,
                                             min=0,
                                             soft_max=10)

    stipple_ao = bpy.props.FloatProperty(name="AO",
                                         description="Desired weighting of ambient occlusion's contribution to the "
                                                     "overall lighting",
                                         precision=1,
                                         default=1,
                                         min=0,
                                         soft_max=10)

    stipple_head_radius = bpy.props.FloatProperty(name="Head Radius",
                                                  description="Head radius of the stipple stroke",
                                                  precision=1,
                                                  default=1,
                                                  min=0,
                                                  soft_max=10,
                                                  subtype="PIXEL")

    stipple_tail_radius = bpy.props.FloatProperty(name="Tail Radius",
                                                  description="Tail radius of the stipple stroke",
                                                  precision=1,
                                                  default=0,
                                                  min=0,
                                                  soft_max=10,
                                                  subtype="PIXEL")

    stipple_length = bpy.props.FloatProperty(name="Length",
                                             description="Length of the stipple stroke, defined as the "
                                                         "distance between the center of the head and tail.",
                                             precision=1,
                                             default=30,
                                             min=0,
                                             soft_max=200,
                                             subtype="PIXEL")

    stipple_density_factor = bpy.props.FloatProperty(name="Density Factor",
                                                     description="The combined light intensity map will be scaled by "
                                                                 "this linear factor prior to computation of stipple placement",
                                                     precision=4,
                                                     default=0.002,
                                                     min=0,
                                                     soft_max=1,
                                                     step=1)

    stipple_min_allowable = bpy.props.FloatProperty(name="Min Intensity",
                                                    description="Floor limit on intensity",
                                                    precision=4,
                                                    default=0.004,
                                                    min=0,
                                                    soft_max=1,
                                                    step=1)

    stipple_density_exponent = bpy.props.FloatProperty(name="Density Exponent",
                                                       description="The combined light intensity map will be scaled by "
                                                                   "this power prior to computation of stipple placement",
                                                       precision=2,
                                                       default=1,
                                                       min=0,
                                                       soft_max=10)


class MainPanel(bpy.types.Panel):
    """Create a Panel in the Render properties window."""

    logger.debug("Instantiating MainPanel...")

    bl_label = "Hand Drawn NPR"
    bl_idname = "RENDER_PT_hdn_main_panel"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "render"

    def draw_header(self, context):
        self.layout.prop(data=context.scene.system_settings,
                         property="is_system_enabled",
                         text="")

    def draw(self, context):
        system_settings = context.scene.system_settings

        self.layout.label("General:")
        self.layout.prop(data=system_settings,
                         property="out_filename")
        self.layout.prop(data=system_settings,
                         property="corner_factor",
                         text="Corner Factor")

        self.layout.separator()

        box = self.layout.box()
        box.label("Silhouette")
        col = box.column(align=True)
        col.prop(data=system_settings,
                 property="silhouette_const")
        col.prop(data=system_settings,
                 property="silhouette_depth")
        col.prop(data=system_settings,
                 property="silhouette_diffuse")
        col.prop(data=system_settings,
                 property="silhouette_curvature")

        self.layout.separator()

        box = self.layout.box()
        box.prop(data=system_settings,
                 property="is_internal_enabled")
        col = box.column(align=True)
        col.prop(data=system_settings,
                 property="internal_const")
        col.prop(data=system_settings,
                 property="internal_depth")
        col.prop(data=system_settings,
                 property="internal_diffuse")
        col.prop(data=system_settings,
                 property="internal_curvature")

        self.layout.separator()

        box = self.layout.box()
        box.prop(data=system_settings,
                 property="is_streamlines_enabled")
        box.prop(data=system_settings,
                 property="streamline_segments")
        col = box.column(align=True)
        col.prop(data=system_settings,
                 property="streamline_const")
        col.prop(data=system_settings,
                 property="streamline_depth")
        col.prop(data=system_settings,
                 property="streamline_diffuse")
        col.prop(data=system_settings,
                 property="streamline_curvature")

        self.layout.separator()

        box = self.layout.box()
        box.prop(data=system_settings,
                 property="is_stipples_enabled")
        col = box.column(align=True)
        col.prop(data=system_settings,
                 property="stipple_head_radius")
        col.prop(data=system_settings,
                 property="stipple_tail_radius")
        col.prop(data=system_settings,
                 property="stipple_length")
        col = box.column(align=True)
        col.prop(data=system_settings,
                 property="stipple_diffuse")
        col.prop(data=system_settings,
                 property="stipple_shadow")
        col.prop(data=system_settings,
                 property="stipple_ao")
        col = box.column(align=True)
        col.prop(data=system_settings,
                 property="stipple_density_factor")
        col.prop(data=system_settings,
                 property="stipple_density_exponent")
        col.prop(data=system_settings,
                 property="stipple_min_allowable")
        box.prop(data=system_settings,
                 property="stipple_threshold")
        box.prop(data=system_settings,
                 property="is_optimisation_enabled")


def register():
    logger.debug("Registering classes...")

    bpy.utils.register_class(CreateCompositorNodeOperator)
    bpy.utils.register_class(DestroyCompositorNodeOperator)
    bpy.utils.register_class(MainPanel)
    bpy.utils.register_class(NPRSystemSettings)
    bpy.types.Scene.system_settings = bpy.props.PointerProperty(type=NPRSystemSettings)


def unregister():
    logger.debug("Unregistering classes...")

    bpy.utils.unregister_class(CreateCompositorNodeOperator)
    bpy.utils.unregister_class(DestroyCompositorNodeOperator)
    bpy.utils.unregister_class(MainPanel)
    bpy.utils.unregister_class(NPRSystemSettings)
    del bpy.types.Scene.system_settings


if __name__ == "__main__":
    register()
