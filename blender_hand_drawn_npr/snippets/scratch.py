from collections import deque
from blender_hand_drawn_npr.point import Point

# C, D, E, F, G, H
# H, I, J, K
# K, L, A, B

# points = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L"]
points = [Point(10, 0), Point(20, 0), Point(30, 0), Point(40, 0), Point(50, 0), Point(60, 0), Point(70, 0), Point(80, 0)]

corners = [2, 4, 6]
print("###", points)

# print("##", points.index("H"))

offset_correction = corners[0]
corrected_indexes = [x - offset_correction for x in corners]

points = deque(points)
points.rotate(-offset_correction)
print("##!", points)

points = list(points)
print("##*", points)


paths = []
for i in range(0, len(corners)):
    if i != len(corners) - 1:
        paths.append(points[corrected_indexes[i]:corrected_indexes[i + 1] + 1])
    else:
        paths.append(points[corrected_indexes[i]:])
print(paths)
