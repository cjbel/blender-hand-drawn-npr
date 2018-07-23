import unittest
import bpy
from . import hand_drawn_npr


class Tests(unittest.TestCase):

    addon_name = hand_drawn_npr.bl_info["name"].lower().replace(" ", "_")

    def setUp(self):
        bpy.ops.wm.addon_enable(module=self.addon_name)

    def tearDown(self):
        bpy.ops.wm.addon_disable(module=self.addon_name)

    def test_registered(self):
        """ Test that the add-on is registered. """
        active_addons = bpy.context.user_preferences.addons
        self.assertTrue(self.addon_name in active_addons)

    def test_main_panel(self):
        """ Test that the main panel is registered. """
        self.assertTrue(hasattr(bpy.types, hand_drawn_npr.MainPanel.bl_idname))

    def test_travis(self):
        """ Test that Travis CI is working, build should fail here. """
        self.assertTrue(False)


# Ref: https://wiki.blender.org/wiki/Tools/Tests/Python
if __name__ == '__main__':
    unittest.main(argv=[__file__])
