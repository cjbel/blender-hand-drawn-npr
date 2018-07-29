"""
This module is limited to bare minimum functionality needed for Blender to acknowledge the add-on.
Calls to Blender-specific modules (e.g. bpy) are delegated elsewhere to avoid "Module Not Found" errors when testing
outside of the Blender environment.
"""

import os
import logging
import tempfile

bl_info = {"name": "Hand Drawn NPR",
           "category": "Render"}

# Log to temporary directory.
log_file = os.path.join(tempfile.gettempdir(), "hand_drawn_npr.log")
logging.basicConfig(level=logging.DEBUG,
                    format="%(asctime)s %(name)s %(levelname)s %(message)s",
                    filename=log_file,
                    filemode="w")
# Set log level for third party modules.
logging.getLogger('PIL').setLevel(logging.WARNING)
logging.getLogger('matplotlib').setLevel(logging.WARNING)

print(bl_info["name"] + " logging path: " + log_file)


def register():
    from . import blender_controller
    blender_controller.register()


def unregister():
    from . import blender_controller
    blender_controller.unregister()
