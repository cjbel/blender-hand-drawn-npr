import numpy as np
from skimage import img_as_float, img_as_uint, img_as_ubyte, io, transform

# data = np.fromfile("/tmp/NS70.asc", dtype=float, count=-1, sep=" ")
image = np.loadtxt("/tmp/NN10.asc", dtype=np.float)
print(np.max(image))
io.imshow(image)
io.show()
print(image)
print(np.where(image==65535))
io.imsave("/tmp/NN10.png", image)