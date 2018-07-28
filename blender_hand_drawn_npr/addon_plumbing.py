if "bpy" in locals():
    print("Reloading modules.")
    import importlib
    importlib.reload(illustrate)
    print("Reloaded modules.")
else:
    print("Importing modules.")
    from . import illustrate
    print("Imported modules.")

import bpy
import os
import tempfile
import logging
from bpy.app.handlers import persistent

# Define expected render passes.
pass_names = [
    "Depth",
    "Normal",
    "UV",
    "AO",
    "IndexOB",
    "DiffDir"
]


@persistent
def process_illustration(dummy):
    logging.debug("Processing illustration...")
    try:
        illustrator = illustrate.Illustrator(tempfile.gettempdir())
    except AttributeError:
        return

    illustrator.illustrate_silhouette()
    illustrator.illustrate_internal_edges()
    illustrator.save()


def toggle_system(self, context):
    if context.scene.system_settings.is_system_enabled:
        logging.debug("Enabling system...")

        bpy.context.scene.render.engine = "CYCLES"  # TODO: Do we really want to force this change on the User here?

        # TODO: Consider making the layer selectable by the User in the GUI, rather than assuming this here.
        layer = bpy.context.scene.render.layers["RenderLayer"]
        logging.debug("Configuring passes for " + layer.name)
        layer.use_pass_normal = True
        layer.use_pass_uv = True
        layer.use_pass_object_index = True
        layer.use_pass_z = True
        layer.use_pass_diffuse_direct = True
        layer.use_pass_ambient_occlusion = True
        bpy.ops.wm.create_npr_compositor_nodes()

        bpy.app.handlers.render_post.append(process_illustration)
    else:
        logging.debug("Disabling system...")

        bpy.ops.wm.destroy_npr_compositor_nodes()

        bpy.app.handlers.render_post.remove(process_illustration)


class CreateCompositorNodeOperator(bpy.types.Operator):
    bl_idname = "wm.create_npr_compositor_nodes"
    bl_label = "Create compositor nodes to write render passes to disk."

    def execute(self, context):
        logging.debug("Executing CreateCompositorNodeOperator...")

        context.scene.use_nodes = True
        tree = bpy.context.scene.node_tree

        # Remove all nodes. TODO: It would be better to save the User's current tree, then we can revert back to it.
        for node in tree.nodes:
            tree.nodes.remove(node)

        # Create nodes.
        render_layer_node = tree.nodes.new(type="CompositorNodeRLayers")
        render_layer_node.location = 0, 0
        file_out_node = tree.nodes.new(type="CompositorNodeOutputFile")
        file_out_node.location = 300, 0

        # Configure image path.
        file_out_node.base_path = tempfile.gettempdir()

        # Configure outputs and link nodes.
        file_out_node.file_slots.clear()
        links = tree.links
        for pass_name in pass_names:
            file_out_node.file_slots.new(name=pass_name)
            links.new(render_layer_node.outputs[pass_name], file_out_node.inputs[pass_name])

        return {'FINISHED'}


class DestroyCompositorNodeOperator(bpy.types.Operator):
    bl_idname = "wm.destroy_npr_compositor_nodes"
    bl_label = "Destroy compositor nodes to write render passes to disk."

    def execute(self, context):
        logging.debug("Executing DestroyCompositorNodeOperator...")

        return {'FINISHED'}


class SystemSettings(bpy.types.PropertyGroup):
    """ Define add-on system settings. """

    logging.debug("Instantiating SystemSettings...")

    is_system_enabled = bpy.props.BoolProperty(name="Enable",
                                               description="Draw stylised strokes using Hand Drawn NPR",
                                               default=False,
                                               update=toggle_system)


class MainPanel(bpy.types.Panel):
    """Create a Panel in the Render properties window."""

    logging.debug("Instantiating MainPanel...")

    bl_label = "Hand Drawn NPR"
    bl_idname = "RENDER_PT_hdn_main_panel"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "render"

    def draw_header(self, context):
        logging.debug("Drawing MainPanel header...")

        self.layout.prop(context.scene.system_settings, "is_system_enabled", text="")

    def draw(self, context):
        logging.debug("Drawing MainPanel...")

        self.layout.label(text="Lorem ipsum dolor sit amet...")


def register():
    logging.debug("Registering classes...")

    bpy.utils.register_class(CreateCompositorNodeOperator)
    bpy.utils.register_class(DestroyCompositorNodeOperator)
    bpy.utils.register_class(MainPanel)
    bpy.utils.register_class(SystemSettings)
    bpy.types.Scene.system_settings = bpy.props.PointerProperty(type=SystemSettings)


def unregister():
    logging.debug("Unregistering classes...")

    bpy.utils.unregister_class(CreateCompositorNodeOperator)
    bpy.utils.unregister_class(DestroyCompositorNodeOperator)
    bpy.utils.unregister_class(MainPanel)
    bpy.utils.unregister_class(SystemSettings)
    del bpy.types.Scene.system_settings


if __name__ == "__main__":
    register()
