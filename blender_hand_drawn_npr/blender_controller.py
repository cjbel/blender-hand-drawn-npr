if "bpy" in locals():
    import importlib
else:
    try:
        from . import illustrate
    except (AttributeError, ImportError):
        pass
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
    "Depth",
    "Normal",
    "UV",
    "Shadow",
    "AO",
    "IndexOB",
    "DiffDir"
]


@persistent
def process_illustration(dummy):
    logger.debug("Processing illustration...")
    try:
        illustrator = illustrate.Illustrator(tempfile.gettempdir())
    except (NameError):
        # This will fail when being called from vanilla Blender during tests due to lack of needed dependencies.
        # Bail out here, since only the internal Blender functionality is tested.
        return

    illustrator.illustrate_silhouette()
    illustrator.save()


def toggle_system(self, context):
    if context.scene.system_settings.is_system_enabled:
        logger.debug("Enabling system...")

        bpy.context.scene.render.engine = "CYCLES"  # TODO: Do we really want to force this change on the User here?

        # Set default resolution.
        bpy.context.scene.render.resolution_x = 3840
        bpy.context.scene.render.resolution_y = 2160
        bpy.context.scene.render.resolution_percentage = 100

        # Disable all anti-aliasing.
        bpy.context.scene.cycles.progressive = 'BRANCHED_PATH'
        bpy.context.scene.cycles.aa_samples = 1
        bpy.context.scene.cycles.preview_aa_samples = 0

        bpy.context.scene.cycles.diffuse_samples = 10
        bpy.context.scene.cycles.ao_samples = 10

        # TODO: Consider making the layer selectable by the User in the GUI, rather than assuming this here.
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

        # Assign a (non-zero) object id to each geometry object in the scene.
        # TODO: Silhouette drawing needs knowledge of the corresponding grey level in the indexOB map, which is
        # based on this index. It would be better to allow the User to select the Subject of the render, then assign
        # it pass index 1, but this will do for now.
        for n, object in enumerate(context.scene.objects):
            if object.type == 'MESH':
                index = n + 1
                logger.debug("Assigning pass index %d to object: %s", index, object.name)
                object.pass_index = n + 1

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

        # Remove all nodes. TODO: It would be better to save the User's current tree, then we can revert back to it.
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


class SystemSettings(bpy.types.PropertyGroup):
    """ Define add-on system settings. """

    logger.debug("Instantiating SystemSettings...")

    is_system_enabled = bpy.props.BoolProperty(name="Enable",
                                               description="Draw stylised strokes using Hand Drawn NPR",
                                               default=False,
                                               update=toggle_system)


class MainPanel(bpy.types.Panel):
    """Create a Panel in the Render properties window."""

    logger.debug("Instantiating MainPanel...")

    bl_label = "Hand Drawn NPR"
    bl_idname = "RENDER_PT_hdn_main_panel"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "render"

    def draw_header(self, context):
        logger.debug("Drawing MainPanel header...")

        self.layout.prop(context.scene.system_settings, "is_system_enabled", text="")

    def draw(self, context):
        logger.debug("Drawing MainPanel...")

        self.layout.label(text="Lorem ipsum dolor sit amet...")


def register():
    logger.debug("Registering classes...")

    bpy.utils.register_class(CreateCompositorNodeOperator)
    bpy.utils.register_class(DestroyCompositorNodeOperator)
    bpy.utils.register_class(MainPanel)
    bpy.utils.register_class(SystemSettings)
    bpy.types.Scene.system_settings = bpy.props.PointerProperty(type=SystemSettings)


def unregister():
    logger.debug("Unregistering classes...")

    bpy.utils.unregister_class(CreateCompositorNodeOperator)
    bpy.utils.unregister_class(DestroyCompositorNodeOperator)
    bpy.utils.unregister_class(MainPanel)
    bpy.utils.unregister_class(SystemSettings)
    del bpy.types.Scene.system_settings


if __name__ == "__main__":
    register()
