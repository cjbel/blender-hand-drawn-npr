import numpy as np
from skimage.util.shape import view_as_windows
A = np.arange(10*10).reshape(10, 10)
print(A)

window_shape = (3, 3)
B = view_as_windows(A, window_shape)
query = (0, 1)
window_coord = (query[0] - 1, query[1] - 1)

print(window_coord)

local_window = B[window_coord]
print(local_window)
print(np.amax(local_window))

