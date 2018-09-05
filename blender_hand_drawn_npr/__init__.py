"""
This module is limited to bare minimum functionality needed for Blender to acknowledge the add-on.
Calls to Blender-specific modules (e.g. bpy) are delegated elsewhere to avoid "Module Not Found" errors when testing
outside of the Blender environment.
"""

bl_info = {"name": "Hand Drawn NPR",
           "category": "Render"}

# Support 'reload' case.
if "bpy" in locals():
    import importlib
    if "properties" in locals():
        importlib.reload(properties)
    if "ui" in locals():
        importlib.reload(ui)
    if "operators" in locals():
        importlib.reload(operators)
    if "engine" in locals():
        importlib.reload(engine)

from .view_controller import (
        properties,
        ui,
        operators,
        )

import os
import logging
import tempfile

# Log to temporary directory.
log_file = os.path.join(tempfile.gettempdir(), "hand_drawn_npr.log")
logging.basicConfig(level=logging.DEBUG,
                    format="%(asctime)s %(name)s %(levelname)s %(message)s",
                    filename=log_file,
                    filemode="w")
# Set log level for third party modules.
logging.getLogger('PIL').setLevel(logging.WARNING)
logging.getLogger('matplotlib').setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

print(bl_info["name"] + " logging path: " + log_file)


def register():
    logger.debug("Registering classes...")

    from .view_controller import operators
    from .view_controller import properties
    from .view_controller import ui

    operators.register()
    properties.register()
    ui.register()

    # bpy.utils.register_class(CreateCompositorNodeOperator)
    # bpy.utils.register_class(DestroyCompositorNodeOperator)
    # bpy.utils.register_class(MainPanel)
    # bpy.utils.register_class(NPRSystemSettings)
    #
    # bpy.types.Scene.system_settings = bpy.props.PointerProperty(type=NPRSystemSettings)


def unregister():
    logger.debug("Unregistering classes...")

    from .view_controller import operators
    from .view_controller import properties
    from .view_controller import ui

    operators.unregister()
    properties.unregister()
    ui.unregister()

    # bpy.utils.unregister_class(CreateCompositorNodeOperator)
    # bpy.utils.unregister_class(DestroyCompositorNodeOperator)
    # bpy.utils.unregister_class(MainPanel)
    # bpy.utils.unregister_class(NPRSystemSettings)
    # del bpy.types.Scene.system_settings
