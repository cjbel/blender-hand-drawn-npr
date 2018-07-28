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

# Log to a temporary directory in a platform-independent way.
log_file = os.path.join(tempfile.gettempdir(), "hand_drawn_npr.log")
logging.basicConfig(level=logging.DEBUG,
                    format="%(asctime)s %(levelname)s %(message)s",
                    filename=log_file,
                    filemode="w")

print(bl_info["name"] + " logging path: " + log_file)


def register():
    from . import addon_plumbing
    addon_plumbing.register()


def unregister():
    from . import addon_plumbing
    addon_plumbing.unregister()
