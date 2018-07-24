import bpy
import os
import tempfile
import logging

# Log to a temporary directory in a platform-independent way.
log_file = os.path.join(tempfile.gettempdir(), "hand_drawn_npr.log")
logging.basicConfig(level=logging.DEBUG,
                    format="%(asctime)s %(levelname)s %(message)s",
                    filename=log_file,
                    filemode="w")

bl_info = {"name": "Hand Drawn NPR", "category": "Render"}

print(bl_info["name"] + " logging path: " + log_file)


def toggle_system(self, context):
    if context.scene.system_settings.is_system_enabled:
        logging.debug("Enabling system...")
        # Register pre and post-render hooks here.
    else:
        logging.debug("Disabling system...")
        # Unregister pre and post-render hooks here.


class SystemSettings(bpy.types.PropertyGroup):
    """ Define add-on system settings. """

    logging.debug("Instantiating SystemSettings...")

    is_system_enabled = bpy.props.BoolProperty(name="Enable",
                                               description="Draw stylised strokes using Hand Drawn NPR.",
                                               default=False,
                                               update=toggle_system)


class MainPanel(bpy.types.Panel):
    """Create a Panel in the Render properties window."""

    logging.debug("Instantiating MainPanel...")

    bl_label = bl_info["name"]
    bl_idname = "RENDER_PT_hdn_main_panel"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "render"

    def draw_header(self, context):
        logging.debug("Drawing MainPanel header...")  # Called frequently during normal use, consider omitting this.

        self.layout.prop(context.scene.system_settings, "is_system_enabled", text="")

    def draw(self, context):
        logging.debug("Drawing MainPanel...")  # Called frequently during normal use, consider omitting this.

        self.layout.label(text="Lorem ipsum dolor sit amet...")


def register():
    logging.debug("Registering classes...")

    bpy.utils.register_class(MainPanel)
    bpy.utils.register_class(SystemSettings)
    bpy.types.Scene.system_settings = bpy.props.PointerProperty(type=SystemSettings)


def unregister():
    logging.debug("Unregistering classes...")

    bpy.utils.unregister_class(MainPanel)
    bpy.utils.unregister_class(SystemSettings)
    del bpy.types.Scene.system_settings


if __name__ == "__main__":
    register()
