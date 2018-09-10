import unittest
import os
import tempfile
import bpy

"""
Note: Module name intentionally doesn't start with "test_", the unittest runner must not run these tests (they must be 
run from within Blender only). 
"""


class BlenderTests(unittest.TestCase):

    addon_name = "blender_hand_drawn_npr"

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


# Ref: https://wiki.blender.org/wiki/Tools/Tests/Python
if __name__ == '__main__':
    unittest.main(argv=[__file__])
