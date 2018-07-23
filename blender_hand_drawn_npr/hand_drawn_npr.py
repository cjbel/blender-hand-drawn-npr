import bpy
import os
import tempfile
import logging

# Log to a temporary directory in a platform-independent way.
log_file = os.path.join(tempfile.gettempdir(), 'hand_drawn_npr.log')
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(message)s',
                    filename=log_file,
                    filemode='w')

bl_info = {"name": "Hand Drawn NPR", "category": "Render"}

print(bl_info['name'] + " logging path: " + log_file)


class MainPanel(bpy.types.Panel):
    """Create a Panel in the Render properties window."""

    logging.debug("Instantiating MainPanel...")

    bl_label = "Hand Drawn NPR"
    bl_idname = "RENDER_PT_hand_drawn_main_panel"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "render"

    def draw(self, context):
        logging.debug("Drawing MainPanel...")  # draw() is called frequently during normal use, consider omitting this.
        self.layout.label(text="Lorem ipsum dolor sit amet...")


def register():
    logging.debug("Registering classes...")

    bpy.utils.register_class(MainPanel)


def unregister():
    logging.debug("Unregistering classes...")

    bpy.utils.unregister_class(MainPanel)


if __name__ == "__main__":
    register()
