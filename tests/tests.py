import unittest
import bpy
import tempfile
import os


class Tests(unittest.TestCase):

    addon_name = "hand_drawn_npr"

    def setUp(self):
        bpy.ops.wm.addon_enable(module=self.addon_name)

    def tearDown(self):
        bpy.ops.wm.addon_disable(module=self.addon_name)

    def test_addon_registered(self):
        """ Test that the add-on is registered. """
        active_addons = bpy.context.user_preferences.addons
        self.assertTrue(self.addon_name in active_addons)

    def test_main_panel(self):
        """ Test that the main panel is registered. """
        panel_idname = "RENDER_PT_hdn_main_panel"
        self.assertTrue(hasattr(bpy.types, panel_idname))

    def test_system_settings_registered(self):
        """ Test that the System Settings have been registered. """
        property_group_name = "system_settings"
        self.assertTrue(hasattr(bpy.types.Scene, property_group_name))

    def test_system_checkbox(self):
        """ Test that the checkbox which enables/disables the system is present. """
        property_name = "is_system_enabled"
        self.assertTrue(hasattr(bpy.context.scene.system_settings, property_name))

    def test_pre_render_hooks(self):
        """ Test that pre-render handlers have been registered. """
        pass

    def test_post_render_hook_process_illustration(self):
        """ Test that process_illustration gets registered as a post-render hook upon enabling the System. """
        handler_name = "process_illustration"
        bpy.context.scene.system_settings.is_system_enabled = True
        self.assertTrue(handler_name in str(bpy.app.handlers.render_post))

    def test_pass_output(self):
        """ Test that a render pass gets written to disk after render. """
        image_filename = os.path.join(tempfile.gettempdir(), "DiffDir0001.png")
        # Remove any old versions.
        try:
            os.remove(image_filename)
        except FileNotFoundError:
            pass
        bpy.context.scene.system_settings.is_system_enabled = True
        bpy.context.scene.cycles.samples = 1
        bpy.ops.render.render()
        self.assertTrue(os.path.isfile(image_filename))


# Ref: https://wiki.blender.org/wiki/Tools/Tests/Python
if __name__ == '__main__':
    unittest.main(argv=[__file__])
