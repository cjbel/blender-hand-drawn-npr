"""
Add-on install script for use with Travis CI.
"""

import bpy

bpy.ops.wm.addon_install(filepath="/home/travis/build/cjbel/blender-hand-drawn-npr/blender_hand_drawn_npr/hand_drawn_npr.py")

