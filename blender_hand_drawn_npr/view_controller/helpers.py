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
    bpy.ops.wm.render_npr()
