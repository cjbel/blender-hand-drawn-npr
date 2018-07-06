# Ref (verbatim): http://scikit-image.org/docs/dev/api/skimage.draw.html#skimage.draw.circle

import numpy as np
from skimage.draw import circle
img = np.zeros((10, 10), dtype=np.uint8)
rr, cc = circle(4, 4, 5)
img[rr, cc] = 1

print(img)
