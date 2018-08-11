from blender_hand_drawn_npr.primitives import Path

path = Path([[10, 0], [20, 0], [30, 0]])
y = path.points[0]
print(y)

dy = [y[i + 1] - y[i] for i in range(len(y) - 1)]
print(dy)