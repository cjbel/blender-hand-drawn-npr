import logging
from collections import namedtuple

import imageio
from skimage import io, exposure
import numpy as np

logger = logging.getLogger(__name__)


class Surface:

    def __init__(self, obj_image=None, z_image=None, diffdir_image=None, norm_image=None, u_image=None, v_image=None):
        self.obj_image = obj_image
        self.z_image = z_image
        self.diffdir_image = diffdir_image
        self.norm_image = norm_image
        self.norm_x = None
        self.norm_y = None
        self.norm_z = None
        self.u_image = u_image
        self.v_image = v_image
        self.u_curvature_image = None
        self.v_curvature_image = None

        self.SurfaceData = namedtuple("SurfaceData", "obj z diffdir norm norm_x norm_y norm_z u v u_curvature v_curvature")

    def init_obj_image(self, file_path):
        self.obj_image = io.imread(file_path, as_gray=True)
        logger.info("Object image loaded: %s", file_path)

    def init_z_image(self, file_path):
        self.z_image = io.imread(file_path, as_gray=True)
        logger.info("Z image loaded: %s", file_path)

    def init_diffdir_image(self, file_path):
        self.diffdir_image = io.imread(file_path, as_gray=True)
        logger.info("Diffdir image loaded: %s", file_path)

    def init_norm_image(self, file_path):
        norm_image = imageio.imread(file_path)
        logger.info("Normal image loaded: %s", file_path)
        # Original image will be mapped to non-linear colourspace. Correct the normals by adjusting this.
        norm_image = exposure.adjust_gamma(norm_image, 2.2)

        # normal x values are encoded in red channel.
        self.norm_x = norm_image[:, :, 0]
        # normal y values are encoded in green channel.
        self.norm_y = norm_image[:, :, 1]
        # normal z values are encoded in blue channel.
        self.norm_z = norm_image[:, :, 2]

        self.norm_image = io.imread(file_path, as_gray=True)

    def init_uv_image(self, file_path):
        # 16-bit colour-depth, use imageio.
        uv_image = imageio.imread(file_path)
        # Original image will be mapped to non-linear colourspace. Correct the uv coordinates by adjusting this.
        uv_image = exposure.adjust_gamma(uv_image, 2.2)

        # u coordinates are encoded in red channel.
        self.u_image = uv_image[:, :, 0]
        # v coordinates are encoded in green channel.
        self.v_image = uv_image[:, :, 1]

        logger.info("UV image loaded: %s", file_path)

        self.u_curvature_image = np.zeros_like(self.obj_image)
        self.v_curvature_image = np.zeros_like(self.obj_image)

    def at_point(self, x, y):
        assert x >= 0
        assert y >= 0

        surface_data = self.SurfaceData(obj=self.obj_image[y, x],
                                        z=self.z_image[y, x],
                                        diffdir=self.diffdir_image[y, x],
                                        norm=self.norm_image[y, x],
                                        norm_x=self.norm_x[y, x],
                                        norm_y=self.norm_y[y, x],
                                        norm_z=self.norm_z[y, x],
                                        u=self.u_image[y, x],
                                        v=self.v_image[y, x],
                                        u_curvature=self.u_curvature_image[y, x],
                                        v_curvature=self.u_curvature_image[y, x])
        return surface_data

    def is_valid(self, point):
        surface_data = self.at_point(point[0], point[1])
        return surface_data.obj != 0

    def compute_curvature(self, path, target_image):

        for i in range(0, len(path.points) - 1):
            cur_norm = self.at_point(path.points[i][0], path.points[i][1]).norm
            next_norm = self.at_point(path.points[i + 1][0], path.points[i + 1][1]).norm

            delta = abs(cur_norm - next_norm)

            if target_image is self.u_image:
                self.u_curvature_image[path.points[i][1], path.points[i][0]] = delta
            elif target_image is self.v_image:
                self.v_curvature_image[path.points[i][1], path.points[i][0]] = delta
            else:
                logger.warning("UV image mismatch!")


if __name__ == "__main__":
    pass
