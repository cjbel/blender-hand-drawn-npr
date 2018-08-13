import math
import numpy as np
import svgpathtools as svgp
from svgpathtools import bezier
from matplotlib import pyplot as plt

d_good1 = "M 299,590 C 375.333,563.333 451.451,536.042 528,510"
d_good2 = "M 170,499 C 435.667,417.667 701.333,336.333 967,255"

d_bad1 = "M 357,388 C 1591.98,1070.49 -325.562,9.66142 622,537"
d_bad2 = "M 551,769 C 3789.23,-656.279 -1562.25,1698.15 1063,546"

ds = [d_good1, d_good2, d_bad1, d_bad2]


for d in ds:
    svgp_path = svgp.parse_path(d)
    for segment in svgp_path:

        dif = np.polyder(segment.poly())
        roots = abs(dif.r.imag)

        print(any(math.isclose(0, root, abs_tol=1e-4) for root in roots))
