from blender_hand_drawn_npr.point_utils import *
import numpy as np





verts = [(3, 0), (5, 0), (7, 0), (9, 0)]
print(verts)
out = rotate_about_xy(verts, 0, 0, 90)
print(np.round(out))
